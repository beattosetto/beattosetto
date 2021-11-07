"""Template filter for beatmap constant.

This template is shared between actual beatmap card and demo card.
In demo card, the input is string while it is int in beatmap card.
"""
from typing import Union
from django import template
from beatmap_collections import constants

register = template.Library()


def get_language_name(language_id: Union[str, int]):
    """Get language from osu! language id."""
    language_id = int(language_id)
    return constants.languages.get(language_id, "Unknown")


def get_genre_name(genre_id: Union[str, int]):
    """Get genre name from osu! genre id."""
    genre_id = int(genre_id)
    return constants.genres.get(genre_id, "Unknown")


# Register filters
register.filter('get_language_name', get_language_name)
register.filter('get_genre_name', get_genre_name)
