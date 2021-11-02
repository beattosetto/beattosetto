import threading
from django.contrib.auth.decorators import user_passes_test
from django.core.checks import messages
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import ActionLog
from .scripts import update_beatmap_action_script


@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def actions(request):
    """View for Action menu."""
    context = {
        'action_log': ActionLog.objects.all().order_by('-id')
    }
    return render(request, 'actions/actions.html', context)


@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def update_beatmap_action(request):
    """
    View for activate the new runner for running update_beatmap_action_script function.

    This view can only activate by superuser and staff.
    """
    action_log = ActionLog()
    action_log.name = "Update all beatmap metadata"
    action_log.running_text = "Start working thread..."
    action_log.status = 1
    action_log.start_user = request.user
    action_log.save()
    action_log.log.save(f"log_{action_log.id}", ContentFile(f'# Log for worker ID : {action_log.id}\n'))
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
    """
    action = get_object_or_404(ActionLog, id=log_id)
    if action.status == 1 or action.status == 0:
        duration = (timezone.now() - action.time_start).total_seconds()
    elif action.status == 2:
        duration = (action.time_finish - action.time_start).total_seconds()
    else:
        duration = "Unknown"

    if duration != "Unknown":
        hours = duration//3600
        duration = duration - (hours*3600)
        minutes = duration//60
        seconds = duration - (minutes*60)
        duration = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))

    if request.method == "GET":
        return JsonResponse({"running_text": action.running_text, "status": action.status, "duration": duration}, status=200)
    return JsonResponse({}, status=400)
