# middleware.py

from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.urls import resolve
from django.conf import settings

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_url = request.path
        exempt_routes = ['/api/register/', '/api/login/']
        if current_url not in exempt_routes:
            auth_header = request.META.get('HTTP_AUTHORIZATION')
            
            if auth_header:
                try:
                    token = auth_header.split()[1]  
                    print(token)
                    jwt_auth = JWTAuthentication()
                    validated_token = jwt_auth.get_validated_token(token)
                    request.user = jwt_auth.get_user(validated_token) 
                except (AuthenticationFailed, IndexError):
                    print('Token inválido o no proporcionado.')
                    return JsonResponse({'detail': 'Token inválido o no proporcionado.'}, status=403)

        response = self.get_response(request)
        return response