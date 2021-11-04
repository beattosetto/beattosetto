import datetime

from django import template

register = template.Library()


def convert_datetime(date: str):
    """
    Converts a datetime string to a human-readable format.
    Args:
        date(str): The datetime string to convert.

    Returns:
        datetime: The converted datetime.
    """
    try:
        return datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return date


register.filter('convert_datetime', convert_datetime)
