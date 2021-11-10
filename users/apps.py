"""
This file manage for Django apps configuration.
"""
from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Class for users app configuration."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        import users.signals
