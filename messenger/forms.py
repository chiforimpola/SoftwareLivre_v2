# -*- coding: utf-8 -*-

from django import forms
from django.contrib.localflavor.br.forms import BRCPFField
from core.models import GenericProfile

class LoginForm(forms.Form):
    email = forms.EmailField(label=u'Email')
    password = forms.CharField(label=u'Senha', widget=forms.PasswordInput())
    next_url = forms.CharField(label=u'Next Url', max_length=200, widget=forms.HiddenInput(), required=False)


class CreateAccountForm (forms.Form):
    def __init__(self, *args, **kw):
        super (CreateAccountForm, self).__init__(*args, **kw)
        self.fields.keyOrder = [
            'full_name',
            'email',
            'password',
            'repeat_password'
        ]
    full_name = forms.CharField (label=u'Nome Completo', max_length=200)
    email = forms.EmailField (label=u'Endereço de email')
    repeat_password = forms.CharField (label=u'Repetir senha', max_length=50, widget=forms.PasswordInput())
    password = forms.CharField (label=u'Senha', max_length=50, widget=forms.PasswordInput())

    def clean_email (self):
        if 'email' in self.cleaned_data:
            email = self.cleaned_data['email']
            if GenericProfile.objects.filter(user__email__iexact=email):
                raise forms.ValidationError (u'Email já existe!')
            return (email)
        raise forms.ValidationError (u'Required Field')

    def clean_password (self):
        if 'password' in self.cleaned_data:
            password = self.cleaned_data['password']
            if len(password) >= 5:
                return (password)
            elif len(password) > 0:
                raise (forms.ValidationError(u'Senha possui menos de 5 dígitos'))
        raise (forms.ValidationError(u'Campo obrgatório'))

    def clean_repeat_password(self):
        data = self.cleaned_data
        if data['password'] == data['repeat_password']:
            return (data['password'])
        raise (forms.ValidationError(u'Senhas não conferem!'))
