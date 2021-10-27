from django import forms
from .models import Profile


class ProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, label='Profile Picture')

    class Meta:
        model = Profile
        fields = ['profile_picture']
