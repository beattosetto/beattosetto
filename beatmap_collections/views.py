"""Views of beatmap collection app."""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from .forms import *
from .functions import *
import random


def random_hero_image():
    """Random the image from hero folder and return the location use in static tag"""
    return f"img/hero/{random.randint(1, 43)}.jpg"


def home(request):
    """The homepage of the website."""
    context = {
        "latest_added": Collection.objects.order_by('-create_date')[:4],
        'hero_image': random_hero_image()
    }
    return render(request, 'beatmap_collections/index.html', context)


def listing(request):
    """The listing page that listing all of the collection in the website."""
    collections = Collection.objects.order_by('name')
    context = {
        "collections": collections,
        'hero_image': random_hero_image()
    }
    return render(request, 'beatmap_collections/listing.html', context)


@login_required
def create_collection(request):
    """View for collection creation page."""
    if request.method == 'POST':
        form = CreateCollectionForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.author = request.user
            form.save()
            messages.success(request, 'Collection created!')
            return redirect("collection", form.instance.id)
    else:
        form = CreateCollectionForm()
    context = {
        'form': form,
        'hero_image': random_hero_image()
    }
    return render(request, 'beatmap_collections/create_collection.html', context)


def collection_page(request, collection_id):
    """View for collection page. It contain all detail of each collection."""
    collection = get_object_or_404(Collection, id=collection_id)
    if request.method == 'POST':
        form = AddCommentForm(request.POST)
        if form.is_valid():
            comment_object = Comment.objects.create(user=request.user)
            comment_object.collection = collection
            comment_object.detail = form.cleaned_data['comment']
            comment_object.save()
            messages.success(request, 'Add comment successfully!')
            return redirect("collection", collection_id)
    else:
        form = AddCommentForm()
    context = {
        'collection': collection,
        'all_beatmap': BeatmapEntry.objects.filter(collection=collection, owner_approved=True),
        'form': form,
        'comment': Comment.objects.filter(collection=collection)
    }
    return render(request, 'beatmap_collections/collection_page.html', context)


@login_required
def add_beatmap(request, collection_id):
    """View for adding beatmap to the collection."""
    collection = get_object_or_404(Collection, id=collection_id)
    if request.method == 'POST':
        form = AddBeatmapForm(request.POST)
        if form.is_valid():
            if BeatmapEntry.objects.filter(beatmap__beatmap_id=form.cleaned_data['beatmap_id'],
                                           collection=collection, owner_approved=True).exists():
                messages.error(request, 'This beatmap is already in this collection!')
                return redirect('collection', collection_id=collection_id)
            if Beatmap.objects.filter(beatmap_id=form.cleaned_data['beatmap_id']).exists():
                beatmap = Beatmap.objects.get(beatmap_id=form.cleaned_data['beatmap_id'])
            else:
                beatmap = create_beatmap(form.cleaned_data['beatmap_id'])
                if beatmap is None:
                    messages.error(request, 'This beatmap does not exist!')
                    return redirect('collection', collection_id=collection_id)
            beatmap_entry = BeatmapEntry.objects.create(author=request.user)
            beatmap_entry.collection = collection
            beatmap_entry.beatmap = beatmap
            beatmap_entry.comment = form.cleaned_data['comment']
            if request.user == collection.author:
                beatmap_entry.owner_approved = True
                beatmap_entry.save()
                messages.success(request, f'Added {beatmap.title} [{beatmap.version}] to collection successfully!')
                return redirect('collection', collection_id=collection_id)
            beatmap_entry.save()
            # pylint: disable=line-too-long
            messages.success(request,
                             f'Added {beatmap.title} [{beatmap.version}] to beatmap approval list! Please wait for cool person name {collection.author.username} to approve it.')
            return redirect('collection', collection_id=collection_id)
    else:
        form = AddBeatmapForm()
    context = {
        'form': form,
        'collection': collection,
        'hero_image': random_hero_image()
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
        'collection': collection,
        'hero_image': random_hero_image()
    }
    return render(request, 'beatmap_collections/edit_collection.html', context)


def manage_beatmap(request, collection_id):
    """Views for manage beatmap."""
    collection = get_object_or_404(Collection, id=collection_id)
    if request.user != collection.author:
        messages.error(request, "Get out! Get out! GET OUT! You idiot.")
        return redirect('collection', collection_id=collection_id)
    context = {
        'collection': collection,
        'all_beatmap': BeatmapEntry.objects.filter(collection=collection, owner_approved=True),
        'hero_image': random_hero_image()
    }
    return render(request, 'beatmap_collections/manage_beatmap.html', context)


@login_required
def beatmap_approval(request, collection_id):
    """View for approve beatmap page that user who is not collection owner want to add to collection."""
    collection = get_object_or_404(Collection, id=collection_id)
    if request.user != collection.author:
        messages.error(request, 'How dare you access this page despite not an owner??? Go away!')
        return redirect('collection', collection_id=collection_id)
    context = {
        'collection': collection,
        'beatmap_approve': BeatmapEntry.objects.filter(collection=collection, owner_approved=False),
        'hero_image': random_hero_image()
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
        return redirect('beatmap_approval', collection_id=collection_id)
    if BeatmapEntry.objects.filter(collection=collection, beatmap__beatmap_id=beatmap_entry.beatmap.beatmap_id,
                                   owner_approved=True).exists():
        messages.error(request, 'This beatmap is already in collection!')
        return redirect('beatmap_approval', collection_id=collection_id)
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
    if beatmap_entry.owner_approved:
        messages.error(request, 'This beatmap is already approved!')
        return redirect('beatmap_approval', collection_id=collection_id)
    beatmap_entry.delete()
    messages.success(request, 'Beatmap denied!')
    return redirect('beatmap_approval', collection_id=collection_id)


@login_required
def delete_beatmap(request, collection_id, beatmap_entry_id):
    """View for delete beatmap entry"""
    collection = get_object_or_404(Collection, id=collection_id)
    beatmap_entry = get_object_or_404(BeatmapEntry, id=beatmap_entry_id)
    if request.user != collection.author:
        messages.error(request, "Hey! That's nonsense")
        return redirect('collection', collection_id=collection_id)
    beatmap_entry.delete()
    messages.success(request, 'Delete beatmap from collection successfully!')
    return redirect('manage_beatmap', collection_id=collection_id)


def collections_by_tag(request, tag):
    """View for collection by tag"""
    collections = Collection.objects.filter(tags__name__in=[tag])
    context = {
        'collections': collections,
        'tag': tag,
        'hero_image': random_hero_image()
    }
    return render(request, 'beatmap_collections/collections_by_tag.html', context)


def collection_embed(request, collection_id):
    """Embed for a collection.

    It's meant to be embedded as iframe tag.
    """
    collection = get_object_or_404(Collection, id=collection_id)
    context = {
        'collection': collection,
    }
    return render(request, 'beatmap_collections/collection_embed.html', context)


def beatmap_embed(request, collection_id, beatmap_entry_id):
    """Embed for a beatmap entry.

    It's meant to be embedded as iframe tag.
    """
    collection = get_object_or_404(Collection, id=collection_id)
    beatmap_entry = get_object_or_404(BeatmapEntry, id=beatmap_entry_id)
    context = {
        'collection': collection,
        'beatmap_entry': beatmap_entry,
    }
    return render(request, 'beatmap_collections/beatmap_embed.html', context)
