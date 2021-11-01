from django.shortcuts import render


def actions(request):
    return render(request, 'actions/actions.html')