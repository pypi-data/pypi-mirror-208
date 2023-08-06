from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import ExternalUser


class SignUpForm(UserCreationForm):
    class Meta:
        model = ExternalUser
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({
            'type': 'text',
            'required': '',
            'aria-label': 'First name',
            'id': 'first_name',
            'name': 'first_name',
            'class': 'form-control',
            'placeholder': 'John',
            'spellcheck': 'false',
            'autocapitalize': 'on',
            'autocomplete': 'off',
            'autofocus': '',
            'maxlength': 100,
        })
        self.fields['last_name'].widget.attrs.update({
            'type': 'text',
            'required': '',
            'aria-label': 'Last Name',
            'id': 'last_name',
            'name': 'last_name',
            'class': 'form-control',
            'placeholder': 'Doe',
            'spellcheck': 'false',
            'autocapitalize': 'on',
            'autocomplete': 'off',
            'autofocus': '',
            'maxlength': 100,
        })
        self.fields['email'].widget.attrs.update({
            'type': 'email',
            'required': '',
            'aria-label': 'Email',
            'id': 'email',
            'name': 'email',
            'class': 'form-control',
            'placeholder': 'johndoe@example.com',
            'autofocus': '',
        })
        self.fields['password1'].widget.attrs.update({
            'type': 'password',
            'required': '',
            'aria-label': 'Password',
            'id': 'password1',
            'name': 'password1',
            'class': 'form-control',
            'placeholder': 'password',
            'autofocus': '',
            'minlength': 6,
            'maxlength': 128,
        })
        self.fields['password2'].widget.attrs.update({
            'type': 'password',
            'required': '',
            'aria-label': 'Password',
            'id': 'password2',
            'name': 'password2',
            'class': 'form-control',
            'placeholder': 'password',
            'autofocus': '',
            'minlength': 6,
            'maxlength': 128,
        })
