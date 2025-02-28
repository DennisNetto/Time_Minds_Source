from django import forms
from django.forms import ModelForm


type1 = (
    ("Active", "Active"),
    ("On Hold", "On Hold"),
    ("Inactive", "Inactive"),
)

type2 = (
    ("7", "N/A"),
)


class ClientForm(forms.Form):
    client_status = forms.ChoiceField(required=False, choices=type1)
    client_fname = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    client_lname = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    client_phone = forms.CharField(required=True, max_length=13, widget=forms.TextInput(attrs={'class': 'form-control'}))
    client_address = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    client_city = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    client_max_hours = forms.IntegerField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    client_km = forms.IntegerField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    client_notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control'}))
    gh_id = forms.CharField(required=False)


class Departmentform(forms.Form):
    dep_code = forms.CharField(required=False, max_length=3, widget=forms.TextInput(attrs={'class': 'form-control'}))
    gh_id = forms.CharField
    dep_status = forms.ChoiceField(required=False, choices=type1)
    dep_name = forms.CharField(required=True, max_length=40, widget=forms.TextInput(attrs={'class': 'form-control'}))
    dep_desc = forms.CharField(required=False, max_length=1500, widget=forms.Textarea(attrs={'class': 'form-control'}))


class GroupHomeform(forms.Form):
    staff_id = forms.CharField(required=False)
    gh_status = forms.ChoiceField(required=False, choices=type1)
    gh_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    gh_phone = forms.CharField(required=False, max_length=13, widget=forms.TextInput(attrs={'class': 'form-control'}))
    gh_address = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    gh_city = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))


class AdminPassChange(forms.Form):
    password1 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
