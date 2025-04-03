from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from .models import User
from django.db import models  

User = get_user_model()

class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, username=None ,password=None, **kwargs):
        try:
            user = User.objects.get(
                models.Q(email=email) | models.Q(username=username)
            )
        except User.DoesNotExist:
            return None
        if user.check_password(password):
            return user
        return None
