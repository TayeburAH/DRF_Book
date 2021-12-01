from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.db import transaction


# call this UserAdminCreationForm, UserAdminChangeForm in your views.py

User = get_user_model()


class UserAdminCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required
    fields, plus a repeated password.
    """
    email = forms.CharField(label='Email', widget=forms.TextInput(attrs={
        'class': 'email',
        'placeholder': 'Enter email'
    }))

    first_name = forms.CharField(required=False, label='First name', widget=forms.TextInput(attrs={
        'class': 'first_name',
        'id': 'first_name-id',
        'placeholder': 'Enter your code here'

    }))

    # Redesigned last_name, so I have to personally save it, must be here
    last_name = forms.CharField(required=False, label='Last name', widget=forms.TextInput(attrs={
        'class': 'zip_code',
        'id': 'zip-id',
        'placeholder': 'Enter last name here'

    }))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={
        'class': 'password1',
        'placeholder': 'Enter password here'
    }))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={
        'class': 'password2',
        'placeholder': 'Enter same password here'
    }))

    class Meta:
        model = User
        fields = []  # add the required field here

    def clean(self):
        '''
        Verify both passwords match.
        '''
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 is not None and password1 != password2:
            self.add_error("password2", "Your passwords must match")
        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.is_customer = True
        user.is_active = True
        user.email = self.cleaned_data["email"].lower()
        user.set_password(self.cleaned_data["password2"])
        user.email = user.email_phone.lower()
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ['email', 'password', 'is_active', 'is_superuser']

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


