from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from django.contrib.auth import authenticate, login, logout

User = get_user_model()


class DrfAuthBackend(BaseAuthentication):
    def authenticate(self, username=None, password=None):
        print('inside DrfAuthBackend')
        print(username)
        print(password)
        try:
            user = User.objects.get(username=username)
            print('Exists')
            if user.check_password(password):
                return user, None
        except User.DoesNotExist:
            print('None')
            return None
