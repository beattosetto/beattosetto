from allauth.socialaccount.models import SocialAccount
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import *
from random_username.generate import generate_username
import random

COOL_SETTINGS_WORD = [
    'Maybe your Discord profile is looking cool!',
    'I know you love Siesta. You can set your cute Siesta here!',
    "Don't just click the circle and abandon your cool profile!",
    'OOoOoooOOooOOO!',
    'But I think your profile is looking cool now!',
    "You love Pepe? That's a good idea! I like Pepe.",
    "And if you ask me how I'm feeling. Don't tell me you're too blind to see."
]


@login_required()
def settings(request):
    if request.method == 'POST':
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        user_form = UserUpdateForm(request.POST, instance=request.user)
        if profile_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, 'Update your cool profile successfully!')
            return redirect("settings")
    else:
        profile_form = ProfileUpdateForm(instance=request.user.profile)
        user_form = UserUpdateForm(instance=request.user)

    if SocialAccount.objects.filter(user=request.user).exists():
        osu_confirm_username = SocialAccount.objects.get(user=request.user).extra_data['username']
    else:
        osu_confirm_username = None

    context = {
        'cool_description': random.choice(COOL_SETTINGS_WORD),
        'random_username': generate_username()[0],
        'profile_form': profile_form,
        'user_form': user_form,
        'social_account': SocialAccount.objects.filter(user=request.user).exists(),
        'osu_confirm_username': osu_confirm_username
    }
    return render(request, 'users/settings.html', context)
