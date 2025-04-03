
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
from django.contrib.auth import authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import User 
from .serializers import UserSerializer, SendEmailSerializer, VerifyCodeSerializer, ResetPasswordSerializer, ResetPasswordResponseSerializer
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import messages


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    
    def perform_create(self, serializer):
        
        serializer.save(is_active=True)


class LoginView(generics.GenericAPIView):
    
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        username = request.data.get('username')
        password = request.data.get('password')
        # print(f"Email: {email}, Password: {password}")
        
        user = None
        if email:
            user = authenticate(request, email=email, password=password)
        elif username:
            user = authenticate(request, username=username, password=password)
        
        
        if user is None:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
        return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)
    


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)
    def put(self, request):
        user = request.user
        print('USEEER', user)
        
        if 'password' in request.data:
            serializer = UserSerializer(user, data=request.data, partial=True)
        else:
            serializer = UserSerializer(user, data=request.data, partial=True)

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
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = user.generate_reset_token()  

            reset_link = request.build_absolute_uri(
                reverse('reset-password', kwargs={'uidb64': uid, 'token': token})
            )
            html_content = render_to_string('recovery_email.html', {'reset_link': reset_link})
            
            email_message = EmailMultiAlternatives(
                'Recuperación de Contraseña',
                'Para restablecer tu contraseña, haz clic en el enlace proporcionado.',  
                'noreply@example.com',
                [user.email]
            )
            email_message.attach_alternative(html_content, "text/html")
            email_message.send()
            
            return Response({'message': 'Código enviado a tu correo electrónico'}, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

def reset_password_view(request, uidb64, token):
    try:
        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=user_id)  
        
        token_status = user.verify_reset_token(token)
        print(token_status)

        if token_status == 'expired' or token_status == False:
            return JsonResponse({'error': 'El enlace ha caducado. Por favor solicita uno nuevo.'}, status=400)
        elif token_status == 'invalid':
            return JsonResponse({'error': 'El enlace es inválido. Por favor verifica e intenta nuevamente.'}, status=400)
        

        if not user.verify_reset_token(token):  
            return render(request, 'reset_password.html', {'error': 'Token incorrecto o expirado'})
        
        return render(request, 'reset_password.html', {'uidb64': uidb64, 'token': token})

    except (User.DoesNotExist, ValueError):
        return render(request, 'reset_password.html', {'error': 'Usuario no encontrado o token inválido'})
    

class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        user_id = force_str(urlsafe_base64_decode(uidb64))
        try:
            user = User.objects.get(id=user_id)

            if not user.verify_reset_token(token):  
                return Response({'error': 'Token incorrecto o expirado'}, status=status.HTTP_400_BAD_REQUEST)

            new_password = request.data.get('new_password')
            user.set_password(new_password)
            user.save()
         
            messages.success(request, 'La contraseña se cambió exitosamente.')
            
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/')) 
        except User.DoesNotExist:
            return Response({'error': 'Token inválido o usuario no encontrado'}, status=status.HTTP_400_BAD_REQUEST)


