"""
Views for using in actions app.
"""
import threading

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.checks import messages
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import ActionLog
from .scripts import update_beatmap_action_script


@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def actions(request):
    """
    View for Action menu.

    This view can only access by superuser and staff.
    """
    context = {
        'action_log': ActionLog.objects.all().order_by('-id'),
        'update_beatmap_running': ActionLog.objects.filter(name="Update all beatmaps metadata", status=1).exists(),
    }
    return render(request, 'actions/actions.html', context)


@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def update_beatmap_action(request):
    """
    View for activate the new runner for running update_beatmap_action_script function.

    This view can only activate by superuser and staff.
    """
    # If this action is already running, return error message.
    if ActionLog.objects.filter(name="Update all beatmaps metadata", status=1).exists():
        messages.error(request, "This action is already running!")
        return redirect('actions')
    # Create a new action log for binding with the worker.
    action_log = ActionLog()
    action_log.name = "Update all beatmaps metadata"
    action_log.running_text = "Start working thread..."
    action_log.status = 1
    action_log.start_user = request.user
    action_log.save()
    action_log.log.save(f"log_{action_log.id}.log", ContentFile(f'# Log for worker ID : {action_log.id}\n'))
    # Start a new thread to work on this action.
    thread_worker = threading.Thread(target=update_beatmap_action_script, args=[action_log])
    thread_worker.setDaemon(True)
    thread_worker.start()
    messages.success(request, f"Start your cute bot successfully! (Log ID : {action_log.id})")
    return redirect('actions')


@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def check_action_log(request, log_id):
    """
    View for API that request in Actions page to check the status of the action log.
    It will return the value that used in live updating the Action status.

    This view can only access by superuser and staff.
    """
    action = get_object_or_404(ActionLog, id=log_id)
    try:
        if action.status == 1 or action.status == 0:
            # The action is running or in idle state, it will return the start time minus the current time in seconds.
            duration = (timezone.now() - action.time_start).total_seconds()
        elif action.status == 2:
            # The action is finished, it will return the duration that tasks is running (fimished - start) in seconds.
            duration = (action.time_finish - action.time_start).total_seconds()
        else:
            # To avoid error in case that task is failed to run, it will return as unknown.
            duration = "Unknown"
    except TypeError:
        # The time will be show as Unknown when action that is finish not have finish time
        duration = "Unknown"

    # If the duration is known, convert it to the readable format.
    if duration != "Unknown":
        hours = duration//3600
        duration = duration - (hours*3600)
        minutes = duration//60
        seconds = duration - (minutes*60)
        duration = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))

    # Return the duration and status of the action.
    if request.method == "GET":
        return JsonResponse({"running_text": action.running_text, "status": action.status, "duration": duration}, status=200)
    return JsonResponse({}, status=400)


@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def delete_action_log(request, log_id):
    """
    View for delete the action log.

    This view can only access by superuser and staff.
    """
    action = get_object_or_404(ActionLog, id=log_id)
    if action.status == 0 or action.status == 1:
        messages.error(request, "Cannot delete the Action log that is running or in idle state!")
        return redirect('actions')
    action.delete()
    messages.success(request, "Delete action log successfully!")
    return redirect('actions')
