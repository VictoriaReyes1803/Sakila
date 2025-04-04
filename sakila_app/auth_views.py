import hashlib
import os
import secrets

from django.shortcuts import render
from rest_framework.views import APIView
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.http import urlsafe_base64_encode
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import User, Staff
from .serializers import StaffSerializer, SendEmailSerializer, VerifyCodeSerializer, ResetPasswordSerializer, ResetPasswordResponseSerializer
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.core.mail import EmailMessage, get_connection, EmailMultiAlternatives
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password

def send_otp(recipient):
    subject = "Código Temporal de Verificación"
    from_email = "no-reply@misuperdominio.site"

    try:
        staff = Staff.objects.get(email=recipient[0])
    except Staff.DoesNotExist:
        return Response({'error': f'Usuario con el correo {recipient[0]} no encontrado'}, status=404)


    otp = ''.join(str(secrets.randbelow(10)) for _ in range(6))
    expiration_time = timezone.now() + timezone.timedelta(minutes=10)
    encrypted_otp = make_password(otp)

    staff.otp_code = encrypted_otp
    staff.otp_expires_at = expiration_time
    staff.save()

    try:
        with get_connection(
                host=settings.RESEND_SMTP_HOST,
                port=settings.RESEND_SMTP_PORT,
                username=settings.RESEND_SMTP_USERNAME,
                #Esta llave es meramente usada para la prueba, despues de revision se eliminara
                password="re_ZmBoyBtH_BVphuhARwDqwKuRq59sPeukw",
                use_tls=True,
        ) as connection:
            email = EmailMessage(
                subject=subject,
                body=f"Tu código temporal es: {otp}\n Este código es válido por 10 minutos.",
                to=recipient,
                from_email=from_email,
                connection=connection
            ).send()
            print('Email sent successfully')
    except Exception as e:
        print('Error sending email:', e)
        return JsonResponse({'error': str(e)}, status=500)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [AllowAny]
    
    def perform_create(self, serializer):
        
        serializer.save(active=True)


class VerifyCodeView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        password = request.data.get('password')

        if not email or not otp or not password:
            return Response({'error': 'Faltan datos requeridos'}, status=400)

        try:
            staff = Staff.objects.get(email=email)
        except Staff.DoesNotExist:
            return Response({'error': f'Usuario con el correo {email} no encontrado'}, status=404)

        if not check_password(otp, staff.otp_code) or timezone.now() > staff.otp_expires_at:
            return Response({'error': 'Código OTP incorrecto o expirado'}, status=400)

        user_authenticate = authenticate(email=email, password=password)

        if user_authenticate:
            staff.otp_code = None
            staff.otp_expires_at = None
            staff.save()
            refresh = RefreshToken.for_user(user_authenticate)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': StaffSerializer(user_authenticate).data
            })


        return Response({'error': 'Credenciales inválidas'}, status=401)


class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')

        try:
            staff = Staff.objects.get(email=email)
        except Staff.DoesNotExist:
            return Response({'error': f'Usuario con el correo {email} no encontrado'}, status=404)

        send_otp([email])
        return Response({'message': 'OTP enviado'}, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = StaffSerializer(user)
        return Response(serializer.data)
    def put(self, request):
        user = request.user
        print('USEEER', user)
        
        if 'password' in request.data:
            serializer = StaffSerializer(user, data=request.data, partial=True)
        else:
            serializer = StaffSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({'error': 'No refresh token provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            response = token.blacklist()
            
            return Response({'message': 'Sesión cerrada correctamente'}, status=status.HTTP_205_RESET_CONTENT)
        except AttributeError as e:
            return Response({'error': f'AttributeError: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Error: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


class SendRecoveryEmailView(generics.GenericAPIView):
    serializer_class = SendEmailSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        
        try:
            staff = Staff.objects.filter(email=email).first()
            if not staff:
                return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
            uid = urlsafe_base64_encode(force_bytes(staff.staff_id))
            token = staff.generate_reset_token()  

            reset_link = request.build_absolute_uri(
                reverse('reset-password', kwargs={'uidb64': uid, 'token': token})
            )
            html_content = render_to_string('recovery_email.html', {'reset_link': reset_link})
            subject = "Recuperación de Contraseña"
            from_email = "no-reply@sakila.site"
            
            with get_connection(
                host=settings.RESEND_SMTP_HOST,
                port=settings.RESEND_SMTP_PORT,
                username=settings.RESEND_SMTP_USERNAME,
                # Esta clave es para pruebas, cambiar o proteger en producción
                password="re_ZmBoyBtH_BVphuhARwDqwKuRq59sPeukw",
                use_tls=True,
            ) as connection:
                email_message = EmailMultiAlternatives(
                    subject=subject,
                    body="Para restablecer tu contraseña, haz clic en el enlace proporcionado.",
                    to=[staff.email],
                    from_email=from_email,
                    connection=connection
                )
                email_message.attach_alternative(html_content, "text/html")
                email_message.send()
                print('Email sent successfully')

            # email_message = EmailMultiAlternatives(
            #     'Recuperación de Contraseña',
            #     'Para restablecer tu contraseña, haz clic en el enlace proporcionado.',  
            #     'noreply@example.com',
            #     [staff.email]
            # )
            # email_message.attach_alternative(html_content, "text/html")
            # email_message.send()
            
            return Response({'message': 'Código enviado a tu correo electrónico'}, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

def reset_password_view(request, uidb64, token):
    try:
        staff_id = force_str(urlsafe_base64_decode(uidb64))
        staff = Staff.objects.get(staff_id=staff_id)  
        
        token_status = staff.verify_reset_token(token)
        print(token_status)

        if token_status == 'expired' or token_status == False:
            return JsonResponse({'error': 'El enlace ha caducado. Por favor solicita uno nuevo.'}, status=400)
        elif token_status == 'invalid':
            return JsonResponse({'error': 'El enlace es inválido. Por favor verifica e intenta nuevamente.'}, status=400)
        

        if not staff.verify_reset_token(token):  
            return render(request, 'reset_password.html', {'error': 'Token incorrecto o expirado'})
        
        return render(request, 'reset_password.html', {'uidb64': uidb64, 'token': token})

    except (User.DoesNotExist, ValueError):
        return render(request, 'reset_password.html', {'error': 'Usuario no encontrado o token inválido'})
    

class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        staff_id = force_str(urlsafe_base64_decode(uidb64))
        try:
            staff = Staff.objects.get(staff_id=staff_id)

            if not staff.verify_reset_token(token):  
                return Response({'error': 'Token incorrecto o expirado'}, status=status.HTTP_400_BAD_REQUEST)

            new_password = request.data.get('new_password')
            staff.set_password(new_password)
            staff.save()
         
            messages.success(request, 'La contraseña se cambió exitosamente.')
            
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/')) 
        except User.DoesNotExist:
            return Response({'error': 'Token inválido o usuario no encontrado'}, status=status.HTTP_400_BAD_REQUEST)


