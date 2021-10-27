from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import *
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
        profile_form = ProfileForm(request.POST, request.FILES)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Update your cool profile successfully!')
            return redirect("home")
    else:
        profile_form = ProfileForm(instance=request.user.profile)
    context = {
        'cool_description': random.choice(COOL_SETTINGS_WORD),
        'profile_form': profile_form
    }
    return render(request, 'users/settings.html', context)
