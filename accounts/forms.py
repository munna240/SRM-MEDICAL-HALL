
from django import forms
from django.contrib.auth.models import User
from .models import UserProfile


class StaffRegistrationForm(forms.Form):

    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100, required=False)
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    phone = forms.CharField(max_length=20)
    address = forms.CharField(widget=forms.Textarea, required=False)
    profile_picture = forms.ImageField(required=False)

    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username']

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")

        return username

    def clean_email(self):
        email = self.cleaned_data['email']

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")

        return email

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get('password') != cleaned_data.get('confirm_password'):
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data


class DoctorRegistrationForm(StaffRegistrationForm):

    qualification = forms.CharField(max_length=255)
    specialization = forms.CharField(max_length=255)
    bmdc_number = forms.CharField(max_length=100)
    signature = forms.ImageField(required=False)
