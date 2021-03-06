"""
This file use to random heart emoji.
"""
from django import template
import random

register = template.Library()


def random_heart_emoji():
    """Return the random heart emoji.

    Returns:
        str: The random heart emoji.
    """
    return random.choice(['๐', '๐', '๐', '๐', '๐', 'โค๏ธ๐งก๐๐๐๐๐ค๐ค๐ค', 'โค', '๏ธ๐งก', '๐', '๐', '๐', '๐',
                          '๐ค', '๐ค', '๐ค'])


register.simple_tag(random_heart_emoji)
