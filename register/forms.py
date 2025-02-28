from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.db import models


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "password1", "password2"]


type1 = (
    ("1", "Worker"),
    ("2", "Supervisor"),
    ("1", "Coordinator"),
    ("1", "Bookkeeper"),
)


class ProfileForm(forms.Form):
    Firstname = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    Lastname = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    Fulladdress = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    City = forms.CharField(required=True, max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    Phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    Notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control'}))
    Usertype = forms.ChoiceField(required=False, choices=type1)


class UserEdit(UserCreationForm):
    class Meta:
        model = User
        fields = ["username"]
