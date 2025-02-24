from django import forms
from django.contrib.auth.models import User
from .models import CustomUser as Profile


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['store_name', 'address', 'image']

