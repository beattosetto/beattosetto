"""
This file manage for Django apps configuration.
"""
from django.apps import AppConfig


class BeatmapCollectionsConfig(AppConfig):
    """Class for BeatmapCollection app configuration."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'beatmap_collections'
