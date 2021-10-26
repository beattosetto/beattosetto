"""Views of beatmap collection app."""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from .forms import *


def home(request):
    """The homepage of the website. It contains a list of beatmaps chosen semi-randomly."""
    collections = Collection.objects.all()
    context = {"collections": collections}
    return render(request, 'beatmap_collections/index.html', context)


@login_required
def create_collection(request):
    if request.method == 'POST':
        form = CreateCollectionForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.author = request.user
            form.save()
            messages.success(request, 'Collection created!')
            return redirect("home")
    else:
        form = CreateCollectionForm()
    context = {
        'form': form,
    }
    return render(request, 'beatmap_collections/create_collection.html', context)


def collection_page(request):
    return render(request, 'beatmap_collections/collection_page.html')

def edit_collection(request):
    return render(request, 'beatmap_collections/edit_collection.html')