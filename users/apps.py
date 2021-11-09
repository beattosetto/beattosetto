"""
This apps.py contain UserConfig class.
"""
from django.apps import AppConfig


class UsersConfig(AppConfig):
    """UserConfig class contain default auto field & import user's signal."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        import users.signals
