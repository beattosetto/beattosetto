from django import template

register = template.Library()


def convert_progress_bar(value):
    """
    Converts float value in database to progress percentage use in progress bar.
    Args:
        value (float): The float value that you want to convert

    Returns:
        float: The converted value that will use in progress bar.
    """
    if float(value) <= 10:
        return float(value/10)*100
    else:
        return 100


register.filter('convert_progress_bar', convert_progress_bar)
