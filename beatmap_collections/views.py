"""Views of beatmap collection app."""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *


def home(request):
    """The homepage of the website. It contains a list of beatmaps chosen semi-randomly."""
    collections = Collection.objects.all()
    context = {"collections": collections}
    return render(request, 'beatmap_collections/index.html', context)


def home(request):
    return render(request, 'beatmap_collections/index.html')


def collection_page(request):
    return render(request, 'beatmap_collections/collection.html')
