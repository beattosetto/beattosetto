from django import template

from actions.models import ActionLog

register = template.Library()


def update_beatmaps_running():
    """Return the status on Actions tasks about updating beatmap metadata Action as JavaScript boolean value"""
    if ActionLog.objects.filter(name="Update all beatmaps metadata", status=1).exists():
        return "true"
    return "false"


register.simple_tag(update_beatmaps_running)
