from django.shortcuts import render
from functions import get_beatmap_detail


def live_beatmap_card(request, beatmap_id):
    """Return an HTTP of the beatmap card"""
    beatmap_card = render(request, 'beatmap_collections/snippets/beatmap_card_demo.html', {'beatmap': get_beatmap_detail(beatmap_id)})
    beatmap_card['Cache_Control'] = 'public, max_age=100000'
    beatmap_card['Vary'] = 'Accept-Encoding'
    return beatmap_card

