from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from .models import Account

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = Account.objects.get(Q(email=username) | Q(phone_number=username))
        except Account.DoesNotExist:
            return None

        # Verify the password
        if user.check_password(password):
            return user

        return None
