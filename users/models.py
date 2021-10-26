from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User


class Profile(models.Model):
    """This model represents a user's profile. It stores the metadata of a user.

    Attributes:
        profile_picture: The profile picture of the user.
        user: The user that this profile belongs to.
    """

    profile_picture = models.ImageField(default='user_list/placeholder.png', upload_to='user_list', validators=[
        FileExtensionValidator(allowed_extensions=['png', 'gif', 'jpg', 'jpeg', 'bmp', 'svg', 'webp'])])
    user = models.OneToOneField(User, on_delete=models.CASCADE)
