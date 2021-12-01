# Build a custom User serializer, to access take json values and convert to models and get stored

from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework import serializers
from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer
import jwt
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from django.contrib.auth.password_validation import validate_password
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
import jwt
from rest_framework.exceptions import AuthenticationFailed
import requests
from rest_framework.authentication import get_authorization_header

User = get_user_model()


# <------------------  Sign up  ---------------------->

class CustomUserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'is_customer')
        extra_kwargs = {'password': {'write_only': True},
                        'is_customer': {'read_only': True}
                        }  # does not show in the view but only in the post form
        # no restriction on the password

    def create(self, validated_data):
        print("Creating")
        user = User.objects.create_user(**validated_data)
        user.is_customer = True
        user.save()
        return user


# Don't use serializers.ModelSerializer as I don't want to link it to any model
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password = serializers.CharField(max_length=128, write_only=True, required=True)
    confirm_password = serializers.CharField(max_length=128, write_only=True, required=True)
    access_token = serializers.CharField(max_length=255, write_only=True, required=True)

    def validate(self, data):

        token = data['access_token']

        # getting Header from response , self.context['request']
        # Token = self.context['request'].headers['Authorization'].split(' ')[-1]
        # print(self.context['request'].headers['content-type'])
        # print(Token)
        try:
            payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms='HS256')

            user_id = payload['user_id']
            user = User.objects.get(pk=user_id)
            print(self.context['request'].user)  # from Authorization bearer earfsessdzzd....
            if not self.context['request'].user == user:
                raise AuthenticationFailed('Your old password was entered incorrectly. Please enter it again.')

        except jwt.ExpiredSignatureError as e:
            return Response({'error': 'Activations link expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as e:
            return Response({'error': 'Invalid Token'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            raise serializers.ValidationError(e)

        if not user.check_password(data['old_password']):
            raise serializers.ValidationError('Your old password was entered incorrectly. Please enter it again.')

        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("The two password fields didn't match.")

        return data

    def save(self, **kwargs):
        password = self.validated_data['new_password']
        user = self.context['request'].user
        user.set_password(password)
        user.save()
        print('saved new user')
        return user


class EmailResetSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=128, write_only=True, required=True)

    def validate_email(self, email):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('Email does not exist')
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = PasswordResetTokenGenerator().make_token(user)
        relative_link = reverse('reset_password', kwargs={'uid': uid, 'token': token})
        current_site = get_current_site(self.context['request'])
        link = str(current_site) + str(relative_link)

        # Email to be sent
        subject = 'Request for password reset'
        # lets Use email_templates
        password_reset_email = "api/password_reset_email.html"
        context = {
            "email": user.email,
            "link": link,
            'protocol': 'http',
            'expired_time': settings.PASSWORD_RESET_TIMEOUT / (60 * 60)
        }
        body = render_to_string(password_reset_email, context)
        try:
            send_mail(subject, body, 'tayebur@canadaeducationbd.com', [email],
                      fail_silently=False)
            # (subject, message, from_email, recipient_list[])
        except BadHeaderError:
            raise serializers.ValidationError('Invalid header found.')
        except Exception as e:
            raise serializers.ValidationError(e)
        return email


class ResetPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password = serializers.CharField(max_length=128, write_only=True, required=True)

    def validate(self, data):
        if data['old_password'] != data['new_password']:
            raise serializers.ValidationError('Password don\'t match')
        # validate_password(data['new_password1'])
        # automatically will send responses
        return data

    def save(self, **kwargs):
        try:
            uid = force_text(urlsafe_base64_decode(self.context['uid']))
            user = User.objects.get(pk=uid)
            if PasswordResetTokenGenerator().check_token(user, self.context['token']):
                user.set_password(self.validated_data['new_password'])
                user.save()
                print('saved')
                return user
            else:
                return Response({"error": "Invalid token"})
        except Exception as e:
            raise serializers.ValidationError(e)
