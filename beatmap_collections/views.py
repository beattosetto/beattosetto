from django.shortcuts import render


def home(request):
    return render(request, 'beatmap_collections/index.html')


def collection_page(request):
    return render(request, 'beatmap_collections/collection.html')
