from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from .models import User
from django.db import models  
from django.contrib.auth.hashers import make_password
import hashlib
from .models import Staff

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

class StaffAuthBackend:
    def authenticate(self, request, username=None, password=None):
        try:
            user = Staff.objects.get(username=username)
            if user.check_password(password):
                return user
        except Staff.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Staff.objects.get(pk=user_id)
        except Staff.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Staff.objects.get(staff_id=user_id)
        except Staff.DoesNotExist:
            return None