from django import template

register = template.Library()


def convert_star_rating(value):
    """
    Converts a star rating to a 2 decimal point float.
    Args:
        value (float): The star rating to convert.

    Returns:
        float: The converted star rating.
    """
    try:
        return round(float(value), 2)
    except ValueError:
        return None


register.filter('convert_star_rating', convert_star_rating)
