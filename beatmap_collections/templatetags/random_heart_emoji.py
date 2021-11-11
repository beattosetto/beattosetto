import random

from django import template

register = template.Library()


def random_heart_emoji():
    """Return the random heart emoji.

    Returns:
        str: The random heart emoji.
    """
    return random.choice(['💖', '💞', '💓', '💗', '💘', '❤️🧡💛💚💙💜🖤🤍🤎', '❤', '️🧡', '💛', '💚', '💙', '💜',
                          '🖤', '🤍', '🤎'])


register.simple_tag(random_heart_emoji)
