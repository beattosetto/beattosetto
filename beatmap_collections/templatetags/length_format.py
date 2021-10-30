from django import template
from time import strftime, gmtime

register = template.Library()


def length_format(length):
    """Convert second to minutes and second. Mainly use in beatmap time length.

    Args:
        length (int): Length of the beatmap in second.

    Returns:
        str: Formatted length of the beatmap.
    """
    if length >= 3600:
        return strftime("%H:%M:%S", gmtime(length))
    return strftime("%M:%S", gmtime(int(length)))


register.filter('length_format', length_format)
