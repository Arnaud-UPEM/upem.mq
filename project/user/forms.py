from django import forms
from django.core.exceptions import ValidationError
from django.db.models import fields

from .models import Auth

class AuthForm (forms.ModelForm):
    class Meta:
        model = Auth
        fields = ('email',)
        error_messages = {
            'email': {
                'required': 'L\'adresse email est déjà utilisé.'
            }
        }


class SignupForm (AuthForm):
    password1 = forms.CharField(min_length=8, max_length=64, widget=forms.PasswordInput)
    password2 = forms.CharField(min_length=8, max_length=64, widget=forms.PasswordInput)

    class Meta(AuthForm.Meta):
        fields = AuthForm.Meta.fields + ('password1', 'password2',)

    def _clean_password (self, password1, password2):
        if password1 != password2:
            raise ValidationError('Les mots de passe sont différents.')
        return password1

    def clean_password2 (self):
        password = self._clean_password(self.cleaned_data['password1'], self.cleaned_data['password2'])
        if password:
            self.cleaned_data['password'] = password
        return password


# Replaced by SignupForm
class LoginForm (forms.Form):
    email = forms.EmailField()
    password1 = forms.CharField(min_length=8, max_length=64, widget=forms.PasswordInput)
    password2 = forms.CharField(min_length=8, max_length=64, widget=forms.PasswordInput)

    def _clean_password (self, password1, password2):
        if password1 != password2:
            raise ValidationError('Les mots de passe sont différents.')
        return password1

    # def clean_password1 (self):
    #     return self._clean_password(self.cleaned_data['password1'], self.cleaned_data['password2'])

    def clean_password2 (self):
        return self._clean_password(self.cleaned_data['password1'], self.cleaned_data['password2'])


