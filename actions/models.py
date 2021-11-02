from django.contrib.auth.models import User
from django.db import models
from beatmap_collections.models import FALLBACK_USER_KEY


class ActionLog(models.Model):
    """
    A model for storing action log.

    Attributes:
        name (str): The name of the action.
        status (int): The status of the action. (0: idle, 1: running, 2:finished, 3:failed)
        running_text (str): The text to display while the action is running.
        time_start (datetime): The time the action started.
        time_end (datetime): The time the action ended.
        user (User): The user who initiated the action.
    """
    name = models.CharField(max_length=100, default="Beattosetto actions")

    status = models.IntegerField(default=0)
    running_text = models.CharField(max_length=100, default="", blank=True)

    time_start = models.DateTimeField(auto_now_add=True)
    time_finish = models.DateTimeField(null=True, blank=True)

    start_user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=FALLBACK_USER_KEY)
