from django import forms
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _
import re

class RegisterForm(forms.Form):
    username = forms.CharField(max_length = 20, required = True)
    account = forms.CharField(max_length=20, required = True, validators=[validate_email]) #驗證email格式
    password = forms.CharField(max_length=255, required = True, widget=forms.PasswordInput()) #PasswordInput欄位不明碼
    re_password = forms.CharField(max_length=255, required = True, widget=forms.PasswordInput()) #PasswordInput欄位不明碼

    def clean_re_password(self): #確認密碼一致還有建立密碼規則
        password = self.cleaned_data['password']
        re_password = self.cleaned_data['re_password']
        pattern = '^(?!.*[^\x21-\x7e])(?=.{4,10})(?=.*[a-zA-Z])(?=.*\d).*$'
        match = re.search(pattern, password)
        if(not match):
            raise forms.ValidationError(_(
            'Password不允許特殊符號、數字、英文字母以外的字元輸入\
            密碼長度4到10個字元\
            至少要有一個大寫或小寫的英文字母\
            至少要有一個0-9的數字'))
        if(password != re_password):
            raise forms.ValidationError(_('密碼不一致!'))
    def clean_username(self): #不准輸入不允許輸入ASCII以外的字元\x00到\x20，以及\x7F到\xFF這個範圍內的都不行
        username = self.clean_data['username']
        pattern = '(?!.*[^\x21-\x7e])'
        match = re.search(pattern, username)
        if(not match):
            raise forms.ValidationError(_('illegal character!'))
    def clean_account(self): #不准輸入不允許輸入ASCII以外的字元\x00到\x20，以及\x7F到\xFF這個範圍內的都不行
        account = self.clean_data['account']
        pattern = '(?!.*[^\x21-\x7e])'
        match = re.search(pattern, account)
        if(not match):
            raise forms.ValidationError(_('illegal character!'))