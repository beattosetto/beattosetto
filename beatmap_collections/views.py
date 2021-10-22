"""Views of beatmap collection app."""

from django.shortcuts import render
from .models import *


def home(request):
    """The homepage of the website. It contains a list of beatmaps chosen semi-randomly."""
    collections = Collection.objects.all()
    context = {"collections": collections}
    return render(request, 'beatmap_collections/index.html', context)


def login_page(request):
    """The login page. This is where users can log into their accounts."""
    return render(request, 'beatmap_collections/login.html')


def register_page(request):
    """The user registration page. Users can register a new account here."""
    return render(request, 'beatmap_collections/register.html')


def collection_page(request):
    """Collection creation page. Users can create a new beatmap collection here."""
    return render(request, 'beatmap_collections/collection.html')
