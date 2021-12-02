"""
Django settings for apiproject project.

Generated by 'django-admin startproject' using Django 3.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
from pathlib import Path
import django_heroku

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-1w0o*p#n@=m2jv%b45pz15*4l%fpmi_n=tnklf^9yv2_fg1h4s'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'rest-api-book.herokuapp.com', 'localhost']

# Application definition

INSTALLED_APPS = [

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'custom_user',
    'api',

    # Rest Framework
    'rest_framework',

    # For Rest API
    'rest_auth',  # pip install django-rest-auth

    # JWT
    'rest_framework_simplejwt',  # pip install djangorestframework-simplejwt
    'rest_framework_simplejwt.token_blacklist',

    # <---   Allauth  --->
    'django.contrib.sites',
    'allauth',  # no need for this , pip install django-allauth
    'allauth.account',
    'allauth.socialaccount',

    'allauth.socialaccount.providers.facebook',  # if you need FB api
    'allauth.socialaccount.providers.google',  # if you need google api

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'apiproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = (
    # Needed to login by email_phone in Django admin, regardless of `allauth`
    'custom_user.backends.EmailBackend',
)

WSGI_APPLICATION = 'apiproject.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

import dj_database_url

db_from_env = dj_database_url.config(conn_max_age=600)
DATABASES['default'].update(db_from_env)

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'custom_user.CustomUser'
# <app_name>.custom_model_name

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Dhaka'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/


MEDIA_ROOT = os.path.join(BASE_DIR, 'api_media')  # For PC storage
# This is where we are going to upload the pictures otherwise will upload in the root directory


MEDIA_URL = '/api_media/'
# or any prefix you choose, creates a folder
# with name api_media in cloudinary
# DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field


from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    # if True, when you refresh using a refresh Token, you get a new access and new refresh Token
    # if False, when you refresh using a refresh Token, you get a new access only
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

REST_FRAMEWORK = {
    # no. of request, Applies to all class
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.ScopedRateThrottle',
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],

    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/min',
        'user': '100/min',
        'my_user': '100/min',

    },

    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'custom_user.custom_drf_backend.DrfAuthBackend',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )

    # pagination
    # 'DEFAULT_PAGINATION_CLASS':
    #     'rest_framework.pagination.LimitOffsetPagination',
    #     'PAGE_SIZE': 100

}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ['email']
EMAIL_HOST_PASSWORD = os.environ['pass']
DEFAULT_FROM_EMAIL = 'no-reply<no_reply@domain.com>'

# PasswordResetTokenGenerator()
PASSWORD_RESET_TIMEOUT = 7200  # must be in seconds

# Check the site ID number from admin
# Must change the site to localhost:8000/
# Must use python manage.py runserver localhost:8000
SITE_ID = 1

# <-------  allauth setting ----------->

# Redirect after login
LOGIN_REDIRECT_URL = '/'  # just use it like this

# Redirect after logout
LOGOUT_REDIRECT_URL = '/'

# Settings for email as username
# By default new account is created with Username(first _name and last_name)
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False

# Create a new account which is linked to a new user in User,but you have
# to set email in user otherwise it will be blank
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'none'  # Don't verify the email account

# <-------allauth end---------->
REST_USE_JWT = True

django_heroku.settings(locals())
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# CLOUDINARY_STORAGE = {
#     'CLOUD_NAME': 'tayebur-cloud',
#     'API_KEY': '178946229634178',
#     'API_SECRET': '9V-2fHr95D1GtBHZzIt4FCndmhs'
# }

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
