"""
Signal for using in account registration & login.
"""
import requests
from allauth.account.signals import user_logged_in
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """When receive the signal that user signed up, it will create Profile that is bind with the User objects"""
    if created:
        Profile.objects.create(user=instance)


@receiver(user_logged_in)
def user_update_information_from_osu_oauth(request, user, **kwargs):
    """Signal when user login using allauth (sign up with osu! account)"""
    profile = Profile.objects.get(user=request.user)
    if SocialAccount.objects.filter(user=request.user).exists() and not request.user.profile.oauth_first_migrate:
        data = SocialAccount.objects.get(user=request.user).extra_data

        if data["avatar_url"] is not None:
            avatar_pic = requests.get(data["avatar_url"])
            avatar_temp = NamedTemporaryFile(delete=True)
            avatar_temp.write(avatar_pic.content)
            avatar_temp.flush()
            profile.profile_picture.save(data["avatar_url"].split('?')[-1], File(avatar_temp), save=True)

        if data["cover_url"] is not None:
            cover_pic = requests.get(data["cover_url"])
            cover_temp = NamedTemporaryFile(delete=True)
            cover_temp.write(cover_pic.content)
            cover_temp.flush()
            profile.cover_image.save(data["cover_url"].split('/')[-1], File(cover_temp), save=True)

        profile.osu_username = data["username"]
        profile.oauth_first_migrate = True
        profile.save()
    else:
        profile.oauth_first_migrate = True
        profile.save()
