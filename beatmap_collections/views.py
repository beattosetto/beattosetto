"""Views of beatmap collection app."""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from .forms import *
from .functions import *


def home(request):
    """The homepage of the website. It contains a list of beatmaps chosen semi-randomly."""
    collections = Collection.objects.all()
    context = {"collections": collections}
    return render(request, 'beatmap_collections/index.html', context)


@login_required
def create_collection(request):
    """View for collection creation page."""
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


def collection_page(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    context = {
        'collection': collection,
        'all_beatmap': BeatmapEntry.objects.filter(collection=collection),
    }
    return render(request, 'beatmap_collections/collection_page.html', context)


@login_required
def add_beatmap(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    if request.method == 'POST':
        form = AddBeatmapForm(request.POST)
        if form.is_valid():
            beatmap_entry = BeatmapEntry.objects.create()
            beatmap_entry.collection = collection
            if BeatmapEntry.objects.filter(beatmap__beatmap_id=form.cleaned_data['beatmap_id'], collection=collection).exists():
                messages.error(request, 'This beatmap is already in this collection!')
                return redirect('collection', collection_id=collection_id)
            else:
                if Beatmap.objects.filter(beatmap_id=form.cleaned_data['beatmap_id']).exists():
                    beatmap_entry.beatmap = Beatmap.objects.get(beatmap_id=form.cleaned_data['beatmap_id'])
                else:
                    created_beatmap = create_beatmap(form.cleaned_data['beatmap_id'])
                    if created_beatmap is None:
                        messages.error(request, 'This beatmap does not exist!')
                        return redirect('collection', collection_id=collection_id)
                    else:
                        beatmap_entry.beatmap = created_beatmap
            beatmap_entry.author = request.user
            beatmap_entry.comment = form.cleaned_data['comment']
            beatmap_entry.save()
            beatmap = Beatmap.objects.get(beatmap_id=form.cleaned_data['beatmap_id'])
            messages.success(request, f'Added {beatmap.title} [{beatmap.version}] to collection successfully!')
            return redirect('collection', collection_id=collection_id)
    else:
        form = AddBeatmapForm()
    context = {
        'form': form,
    }
    return render(request, 'beatmap_collections/add_beatmap.html', context)


@login_required
def edit_collection(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    if request.user != collection.author:
        messages.error(request, 'BAKA! You are not the author of this collection!')
        return redirect('collection', collection_id=collection_id)
    else:
        if request.method == 'POST':
            form = CreateCollectionForm(request.POST, request.FILES, instance=collection)
            if form.is_valid():
                form.instance.author = request.user
                form.save()
                messages.success(request, 'Edit collection complete!')
                return redirect("collection", collection_id)
        else:
            form = CreateCollectionForm(instance=collection)
        context = {
            'form': form,
            'collection': collection
        }
        return render(request, 'beatmap_collections/edit_collection.html', context)
