from django.shortcuts import render


def home(request):
    return render(request, 'beatmap_collections/index.html')


def login_page(request):
    return render(request, 'beatmap_collections/login.html')


def register_page(request):
    return render(request, 'beatmap_collections/register.html')
