"""
This file use to convert value in database to value that show in infobox.
"""
from django import template

register = template.Library()


def convert_beatmap_stat(value):
    """
    Converts float value from database to value that use to show in infobox.
    Args:
        value (float): Value from database that you want to convert.

    Returns:
        str: Value that use to show in infobox.
    """
    try:
        if (float(value)).is_integer():
            return int(value)
        return round(float(value), 1)
    except ValueError:
        return value


register.filter('convert_beatmap_stat', convert_beatmap_stat)
