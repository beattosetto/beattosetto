"""
This apps.py is for Django apps configuration.
"""
from django.apps import AppConfig


class ActionsConfig(AppConfig):
    """Class for actions app configuration."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'actions'
