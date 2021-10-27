from django.dispatch import receiver
from .models import Profile
from django.db.models.signals import post_save
from django.contrib.auth.models import User


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """When receive the signal that user signed up, it will create Profile that is bind with the User objects"""
    if created:
        Profile.objects.create(user=instance)
