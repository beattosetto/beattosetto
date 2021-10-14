from django.shortcuts import render


def home(request):
    return render(request, 'beatmap_collections/index.html')
