"""
Views for using in users app.
"""
from allauth.socialaccount.models import SocialAccount
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from beatmap_collections.models import Collection
from .forms import *
from random_username.generate import generate_username
import random
from beatmap_collections.views import random_hero_image

COOL_SETTINGS_WORD = [
    'Maybe your Discord profile is looking cool!',
    'I know you love Siesta. You can set your cute Siesta here!',
    "Don't just click the circle and abandon your cool profile!",
    'OOoOoooOOooOOO!',
    'But I think your profile is looking cool now!',
    "You love Pepe? That's a good idea! I like Pepe.",
    "And if you ask me how I'm feeling. Don't tell me you're too blind to see.",
    "I love osu! so much. I want to try it but I doesn't try it yet. Overall I should tried it,"
    " But I still not try it. I hope someday I will have try it except I didn't try it - Some random member."
]

ITEMS_PER_PAGE = 10


@login_required()
def settings(request):
    """Update user's profile data."""
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
        'osu_confirm_username': osu_confirm_username,
        'hero_image': random_hero_image()
    }
    return render(request, 'users/settings.html', context)


def profile(request, user_id: int):
    """View for profile page."""
    profile_owner = get_object_or_404(User, pk=user_id)
    profile_object = profile_owner.profile
    collections = Collection.objects.filter(author=profile_owner).order_by('-create_date')
    page = request.GET.get('page', 1)
    paginator = Paginator(collections, ITEMS_PER_PAGE)
    try:
        collections = paginator.page(page)
    except PageNotAnInteger:
        collections = paginator.page(1)
    except EmptyPage:
        collections = paginator.page(paginator.num_pages)
    # Try to get rid of error from API value
    try:
        if SocialAccount.objects.filter(user=profile_owner).exists():
            osu_username = SocialAccount.objects.get(user=profile_owner).extra_data["username"]
        else:
            osu_username = None
    except KeyError:
        osu_username = None
    context = {
        'profile_owner': profile_owner,
        'profile': profile_object,
        'collections': collections,
        'osu_username': osu_username
    }
    return render(request, "users/profile.html", context)
