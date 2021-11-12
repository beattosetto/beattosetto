"""
This file use to get the filename of the random hero image from static/img/hero folder.
"""
from django import template
import random

register = template.Library()


def get_random_hero_image():
    """Return the filename of the picture that use in header or website's header."""
    return f"img/hero/{random.randint(1,42)}.jpg"


register.simple_tag(get_random_hero_image)
