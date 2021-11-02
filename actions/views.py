import threading

from django.contrib.auth.decorators import user_passes_test
from django.core.checks import messages
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ActionLog
from .scripts import *


@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def actions(request):
    context = {
        'action_log': ActionLog.objects.all().order_by('-id')
    }
    return render(request, 'actions/actions.html', context)


@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def update_beatmap_action(request):
    """
    View for activate the new runner for running update_all_beatmap_action function.

    This view can only activate by superuser and staff. Mainly activate by Maintainer menu.

    :param request: WSGI request from user.
    :return: Redirect to maintainer menu with message
    """
    action_log = ActionLog()
    action_log.title = "Update all beatmap metadata"
    action_log.running_text = "Start working thread..."
    action_log.status = 1
    action_log.start_user = request.user
    action_log.save()
    thread_worker = threading.Thread(target=update_beatmap_action_script, args=[action_log])
    thread_worker.setDaemon(True)
    thread_worker.start()
    messages.success(request, f"Start your cute bot successfully! (Log ID : {action_log.id})")
    return redirect('actions')
