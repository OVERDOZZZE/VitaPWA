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


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label='Имя')
    email = forms.EmailField(label='Электронная почта')
    address = forms.CharField(max_length=100, label='Адрес', required=False)
    store_name = forms.CharField(max_length=100, label='Название', required=False)
    phone_number = forms.CharField(max_length=100, label='Номер телефона', required=False)
    message = forms.CharField(widget=forms.Textarea, label='Дополнительное сообщение', required=False)
