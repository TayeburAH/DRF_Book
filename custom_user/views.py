from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from django.contrib.auth.models import update_last_login
from .models import CustomUser
from .serializes import CustomUserRegistrationSerializer, ChangePasswordSerializer, ResetPasswordSerializer, \
    EmailResetSerializer
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.urls import reverse
from django.contrib.auth import login as login_user, logout as logout_user, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .renderers import UserRenderer


User = get_user_model()


# Create your views here.

# <---------------------------- JWT Authentication is used ----------------------------------------->

class CustomUserSignupView(ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserRegistrationSerializer
    renderer_classes= (UserRenderer, )
    # permission_classes = (IsAuthenticated, IsAdminUser)

    def get(self, request, *args, **kwargs):
        # only superuser can view this
        # if request.user.is_superuser:
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        # else:
        #     dict = {
        #         'message': 'You must be Admin to view this'
        #     }
        #     return Response(dict, status=status.HTTP_204_NO_CONTENT)

    def post(self, request, *args, **kwargs):
        print('Signing up new user')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # what error found during saving in models are shown
        serializer.save()
        user = User.objects.get(email=serializer.data['email'])
        token = user.create_jwt_token
        response = {
            'success': 'True',
            'status code': status.HTTP_200_OK,
            'message': 'Signup complete',
            'token': token,
        }
        return Response(response, status=status.HTTP_200_OK)


class CustomUserAccountChange(RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()  # returns user when called save()
        refresh = RefreshToken.for_user(user)
        response = {
            'success': 'True',
            'status code': status.HTTP_200_OK,
            'message': 'Password changed successfully',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        return Response(response, status=status.HTTP_200_OK)


@api_view(('POST',))  # body ==> request.data
@renderer_classes((UserRenderer, ))
def login(request):
    email = request.data.get('email', None)
    password = request.data.get('password', None)
    # breakpoint()
    if User.objects.filter(email=email).exists():
        # bool(User.objects.get(username=username))
        # will not work as get will return User.DoesNotExist
        user = User.objects.get(email=email)
        if user.check_password(password):
            update_last_login(None, user)
            token = user.create_jwt_token
            response = {
                'success': 'True',
                'status code': status.HTTP_200_OK,
                'message': 'logged in successfully',
                'token': token,
            }
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = {
                'message': 'password incorrect',
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
    else:
        response = {
            'message': 'username does not exist',
        }
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


@api_view(('POST',))
@permission_classes([IsAuthenticated])
def logout(request):
    email = request.data.get('email', None)
    refresh = request.data.get('refresh', None)
    if User.objects.filter(email=email).exists():
        # bool(User.objects.get(username=username))
        # will not work as get will return User.DoesNotExist
        user = User.objects.get(email=email)
        if request.user.is_authenticated and request.user == user:
            token = RefreshToken(refresh)
            token.blacklist()
            # Code to remove tokens from client side
            response = {
                'success': 'True',
                'status code': status.HTTP_200_OK,
                'message': 'logout in successfully',
            }
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = {
                'error': 'check you are logged in',
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    else:
        response = {
            'error': 'Invalid refresh token or user',
        }
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


# EmailResetSerializer
# Send email
@api_view(('POST',))
def reset_password_email(request):
    context = {
        'request': request
    }
    serializer = EmailResetSerializer(data=request.data, context=context)
    serializer.is_valid(raise_exception=True)
    # here's there is noting to save, serializer.save()
    dict = {
        'message': 'An email is sent to you in you email'
    }
    return Response(dict)


# ResetPasswordSerializer
@api_view(('POST',))
def reset_password(request, uid, token):
    context = {
        'request': request,
        'uid': uid,
        'token': token,
    }
    serializer = ResetPasswordSerializer(data=request.data, context=context, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    dict = {
        'message': 'Password has been reset'
    }
    return Response(dict)


from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from rest_auth.registration.views import SocialLoginView
from rest_auth.registration.views import SocialConnectView


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter

    @property
    def callback_url(self):
        # use the same callback url as defined in your GitHub app, this url
        # must be absolute:
        print('self.request.build_absolute_uri')
        print(self.request.build_absolute_uri(reverse('facebook_callback')))
        return self.request.build_absolute_uri(reverse('facebook_callback'))


import urllib.parse

from django.shortcuts import redirect


def facebook_callback(request):
    print('request.GET')
    print(request.GET)
    params = urllib.parse.urlencode(request.GET)
    print('params')
    print(params)
    return redirect(f'http://localhost:8000/accounts/facebook/login/callback/?{params}')

#
# class FacebookConnect(SocialConnectView):
#     adapter_class = FacebookOAuth2Adapter
