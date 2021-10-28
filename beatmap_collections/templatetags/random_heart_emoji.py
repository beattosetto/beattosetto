from django import template
import random

register = template.Library()


def random_heart_emoji():
    """Return the random heart emoji.

    Returns:
        str: The random heart emoji.
    """
    return random.choice(['💖', '💞', '💓', '💗', '💘', '❤️🧡💛💚💙💜🖤🤍🤎', '❤', '️🧡', '💛', '💚', '💙', '💜',
                          '🖤', '🤍', '🤎'])


register.filter('random_heart_emoji', random_heart_emoji)
