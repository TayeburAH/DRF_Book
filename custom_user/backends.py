from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class EmailBackend(ModelBackend):
    """
        This is a ModelBacked that allows authentication with either a username or an email address.
        Authentication backend which allows users to authenticate using either their
        username or email address
        Source: https://stackoverflow.com/a/35836674/59984
        """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # n.b. Django <2.1 does not pass the `request`
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        '''
        The `username` field is allows to contain `@` characters so
        technically a given email address could be present in either field,
        possibly even for different users, so I'll query for all matching
        records and test each one.
        '''
        try:
            user = User.objects.get(email__iexact=username)
            if user.check_password(password):
                return user

        except User.DoesNotExist:
            '''
            skip return None as if a user does not exist the authenticate() 
            function returns None nearly instantaneously.
            That is why run the default password hasher once to increase the timing
            difference between an existing and a non-existing user (#20760).
            so that an attacker would then be able to tell the difference between an 
            existing and a non-existing username.  
            '''
            User().set_password(password)  # takes a longer time
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
