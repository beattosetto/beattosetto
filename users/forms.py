from django import forms
from django.contrib.auth.models import User
from .models import Profile


class ProfileUpdateForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, label='Profile Picture')

    class Meta:
        model = Profile
        fields = ['profile_picture']


class UserUpdateForm(forms.ModelForm):
    """Form in user's settings page to update value in default Django User model."""
    email = forms.EmailField(required=False, label='Email')
    username = forms.CharField(required=True, label='Username')

    class Meta:
        model = User
        fields = ['username', 'email']
