"""
This file contain form class that get the user input from template to views.
"""
from django import forms
from django.contrib.auth.models import User

from .models import Profile


class ProfileUpdateForm(forms.ModelForm):
    """Form in user's settings page to update image of that user."""
    profile_picture = forms.ImageField(required=False, label='Profile Picture')
    cover_image = forms.ImageField(required=False, label='Cover Image')

    class Meta:
        """Create field that contain profile picture & cover image."""
        model = Profile
        fields = ['profile_picture', 'cover_image']


class UserUpdateForm(forms.ModelForm):
    """Form in user's settings page to update value in default Django User model."""
    email = forms.EmailField(required=False, label='Email')
    username = forms.CharField(required=True, label='Username')

    class Meta:
        """Create field that contain username & email."""
        model = User
        fields = ['username', 'email']
