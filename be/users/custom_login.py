from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.utils.translation import gettext_lazy as _


class EmailBackend(ModelBackend):
    """
    With help of this class, we get email instead of username when user wants to login
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            # note than email should not be key sensitive
            user_email = username.lower()
            if '@gmail.com' in user_email:  # in case email is gmail, soroushmehraban and soroush.mehraban should be
                # the same
                gmail_username = user_email.split("@gmail.com")[0]
                gmail_username_sections = gmail_username.split(".")
                gmail_username = "".join(gmail_username_sections)
                user_email = f"{gmail_username}@gmail.com"

            user = UserModel.objects.get(email=user_email)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None


class CustomAuthenticationForm(AuthenticationForm):
    """
    With help of this class, we change the default 'Username' field on login view
    and change the label to 'Email address'
    """
    username = UsernameField(
        label=_('Email Address '),
        widget=forms.TextInput(attrs={'autofocus': True})
    )

    def __init__(self, *args, **kwargs):
        self.error_messages['invalid_login'] = 'Please enter a correct username and password. Note that password ' \
                                               'field is case-sensitive. '
        super().__init__(*args, **kwargs)
