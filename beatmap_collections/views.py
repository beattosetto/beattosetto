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
    """View for collection page. It contain all detail of each collection."""
    collection = get_object_or_404(Collection, id=collection_id)
    context = {
        'collection': collection,
        'all_beatmap': BeatmapEntry.objects.filter(collection=collection, owner_approved=True),
    }
    return render(request, 'beatmap_collections/collection_page.html', context)


@login_required
def add_beatmap(request, collection_id):
    """View for adding beatmap to the collection."""
    collection = get_object_or_404(Collection, id=collection_id)
    if request.method == 'POST':
        form = AddBeatmapForm(request.POST)
        if form.is_valid():
            beatmap_entry = BeatmapEntry.objects.create()
            beatmap_entry.collection = collection
            if BeatmapEntry.objects.filter(beatmap__beatmap_id=form.cleaned_data['beatmap_id'], collection=collection).exists():
                messages.error(request, 'This beatmap is already in this collection!')
                return redirect('collection', collection_id=collection_id)
            if Beatmap.objects.filter(beatmap_id=form.cleaned_data['beatmap_id']).exists():
                beatmap_entry.beatmap = Beatmap.objects.get(beatmap_id=form.cleaned_data['beatmap_id'])
            else:
                created_beatmap = create_beatmap(form.cleaned_data['beatmap_id'])
                if created_beatmap is None:
                    messages.error(request, 'This beatmap does not exist!')
                    return redirect('collection', collection_id=collection_id)
                beatmap_entry.beatmap = created_beatmap
            beatmap_entry.author = request.user
            beatmap_entry.comment = form.cleaned_data['comment']
            if request.user == collection.author:
                beatmap_entry.owner_approved = True
                beatmap_entry.save()
                beatmap = Beatmap.objects.get(beatmap_id=form.cleaned_data['beatmap_id'])
                messages.success(request, f'Added {beatmap.title} [{beatmap.version}] to collection successfully!')
                return redirect('collection', collection_id=collection_id)
            beatmap_entry.save()
            beatmap = Beatmap.objects.get(beatmap_id=form.cleaned_data['beatmap_id'])
            messages.success(request, f'Added {beatmap.title} [{beatmap.version}] to beatmap approval list for this collection! Please wait for collection owner to approve it.')
            return redirect('collection', collection_id=collection_id)
    else:
        form = AddBeatmapForm()
    context = {
        'form': form,
        'collection': collection,
    }
    return render(request, 'beatmap_collections/add_beatmap.html', context)


@login_required
def edit_collection(request, collection_id):
    """View for editing collection."""
    collection = get_object_or_404(Collection, id=collection_id)
    if request.user != collection.author:
        messages.error(request, 'BAKA! You are not the author of this collection!')
        return redirect('collection', collection_id=collection_id)
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


@login_required
def beatmap_approval(request, collection_id):
    """View for approve beatmap page that user who is not collection owner want to add to collection."""
    collection = get_object_or_404(Collection, id=collection_id)
    if request.user != collection.author:
        messages.error(request, 'How dare you access this page despite not an owner??? Go away!')
        return redirect('collection', collection_id=collection_id)
    context = {
        'collection': collection,
        'beatmap_approve': BeatmapEntry.objects.filter(collection=collection, owner_approved=False)
    }
    return render(request, 'beatmap_collections/beatmap_approval.html', context)


@login_required
def approve_beatmap(request, collection_id, beatmap_entry_id):
    """View for approve BeatmapEntry to the collection by changing the owner_approved value to True"""
    collection = get_object_or_404(Collection, id=collection_id)
    beatmap_entry = get_object_or_404(BeatmapEntry, id=beatmap_entry_id)
    if request.user != collection.author:
        messages.error(request, 'Hehehehe No! Stop there!')
        return redirect('collection', collection_id=collection_id)
    if beatmap_entry.owner_approved:
        messages.error(request, 'This beatmap is already approved!')
        return redirect('collection', collection_id=collection_id)
    beatmap_entry.owner_approved = True
    beatmap_entry.save()
    messages.success(request, 'Beatmap approved!')
    return redirect('beatmap_approval', collection_id=collection_id)


@login_required
def deny_beatmap(request, collection_id, beatmap_entry_id):
    """View for deny BeatmapEntry to the collection by deleting the BeatmapEntry object"""
    collection = get_object_or_404(Collection, id=collection_id)
    beatmap_entry = get_object_or_404(BeatmapEntry, id=beatmap_entry_id)
    if request.user != collection.author:
        messages.error(request, 'Hehehehe No! Stop there!')
        return redirect('collection', collection_id=collection_id)
    beatmap_entry.delete()
    messages.success(request, 'Beatmap denied!')
    return redirect('beatmap_approval', collection_id=collection_id)
