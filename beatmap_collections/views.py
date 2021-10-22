"""Views of beatmap collection app."""

from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
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


@login_required
def create_collection_page(request):
    """Collection creation page. Logged in users can create a new beatmap collection here."""
    return render(request, 'beatmap_collections/collection.html')


def save_collection(request):
    """Save a collection to the database."""
    if request.POST['inputTitle']:
        name, description = request.POST['inputTitle'], request.POST['inputDescription']
        collection_object = Collection(name=name, description=description)
        collection_object.save()
        return redirect(reverse('home'))
    return redirect(reverse('new_collection'))
