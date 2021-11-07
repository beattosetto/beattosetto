from django import template

register = template.Library()


def convert_to_float(value):
    """
    Converts a string to a float.

    Arguments:
        value (string) : The string to convert.

    Returns:
        float : The converted float.
    """
    try:
        return float(value)
    except ValueError:
        return value


register.filter('convert_to_float', convert_to_float)
