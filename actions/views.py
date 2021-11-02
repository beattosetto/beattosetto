from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from .models import ActionLog


@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def actions(request):
    context = {
        'action_log': ActionLog.objects.all().order_by('-id')
    }
    return render(request, 'actions/actions.html', context)