from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import models, transaction
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from rest_framework_simplejwt.tokens import RefreshToken

from .custom_validator import *
from django.conf import settings
import re

User = settings.AUTH_USER_MODEL


# Create your models here.

# <------------------  Manager ------------------------->
class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email and password.
        You need to use validation
        """
        user = self.model(
            email=email,
        )

        user.set_password(password)  # or put it in   user = self.model( password = password)
        user.is_staff = False
        user.is_admin = False
        user.is_customer = False
        user.is_seller = False
        user.is_active = True
        # last save it
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        No need to validate
        """

        user = self.create_user(
            email=email,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.is_customer = True
        user.is_seller = True

        # last save it
        user.save(using=self._db)
        return user


# <------------------   User ------------------------->

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.CharField(verbose_name='Email', max_length=50, unique=True, validators=[validate_emails, ])
    date_joined = models.DateField(verbose_name='date joined',
                                   auto_now_add=True)  # when custom_account gets created the date gets set
    last_joined = models.DateField(verbose_name='last joined',
                                   auto_now=True)  # when custom_account gets created the date gets set

    first_name = models.CharField(max_length=60, null=True, blank=True)
    last_name = models.CharField(max_length=60, null=True, blank=True)

    # Must include
    is_active = models.BooleanField(default=True)  # only this true
    is_staff = models.BooleanField(default=False)  # a admin user; non super-user
    is_superuser = models.BooleanField(default=False)  # a superuser

    # add more multi_user
    is_customer = models.BooleanField(default=False)  # a customer
    is_seller = models.BooleanField(default=False)  # a seller

    # notice the absence of a "Password field", id, last_login that is built in.

    objects = UserManager()  # To link it with UserManager(BaseUserManager)

    USERNAME_FIELD = 'email'

    # REQUIRED_FIELDS = ['username']  # Besides email what must be required

    def __str__(self):
        return self.email  # Django uses this when it needs to convert the object into string

    def get_full_name(self):
        # The user is identified by their email address
        return f"{self.first_name} {self.last_name}"

    # add more function here

    # Must be included
    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def create_jwt_token(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


'''
AUTH_USER_MODEL = 'custom_account.CustomUser'    #<app_name>.custom_model_name
change from built-in user model to ours
'''

'''
Now you can't use  from django.contrib.auth.models import User
but you have to use 

from django.conf import settings
User = settings.AUTH_USER_MODEL
'''
