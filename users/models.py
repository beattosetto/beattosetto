"""
Model for users app.
"""
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models
from PIL import Image


class Profile(models.Model):
    """This model represents a user's profile. It stores the metadata of a user.

    Attributes:
        profile_picture: The profile picture of the user.
        cover_image: The profile's cover image.
        user: The user that this profile belongs to.
        osu_username: Username of the osu! account associated with the user.
    """

    profile_picture = models.ImageField(default='user_list/placeholder.png', upload_to='user_list', validators=[
        FileExtensionValidator(allowed_extensions=['png', 'gif', 'jpg', 'jpeg', 'bmp', 'svg', 'webp'])])
    cover_image = models.ImageField(default='cover_list/placeholder.jpg', upload_to='cover_list', validators=[
        FileExtensionValidator(allowed_extensions=['png', 'gif', 'jpg', 'jpeg', 'bmp', 'svg', 'webp'])])
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    osu_username = models.CharField(max_length=32, blank=True)
    oauth_first_migrate = models.BooleanField(default=False)

    def __str__(self):
        """Returns the string representation of the profile."""
        return f"{self.user.username} Profile"

    def save(self, *args, **kwargs):
        """Overrides the save method to resize the profile picture."""
        super().save(*args, **kwargs)
        profile_image = Image.open(self.profile_picture.path)
        if profile_image.height > 300 or profile_image.width > 300:
            profile_image.thumbnail((300, 300))
            profile_image.save(self.profile_picture.path)

        cover_image = Image.open(self.cover_image.path)
        if cover_image.height > 1080 or cover_image.width > 1920:
            cover_image.thumbnail((1920, 1080))
            cover_image.save(self.cover_image.path)
