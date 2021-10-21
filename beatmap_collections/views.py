from django.shortcuts import render
from .models import *


def home(request):
    collections = Collection.objects.all()
    context = {"collections": collections}
    return render(request, 'beatmap_collections/index.html', context)


def login_page(request):
    return render(request, 'beatmap_collections/login.html')


def register_page(request):
    return render(request, 'beatmap_collections/register.html')


def collection_page(request):
    return render(request, 'beatmap_collections/collection.html')
