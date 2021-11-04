from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from .functions import get_beatmap_detail


@login_required
def live_beatmap_card(request, beatmap_id):
    """Return an HTTP of the beatmap card"""
    beatmap_detail = get_beatmap_detail(beatmap_id)
    if beatmap_detail:
        beatmap_card = render(request, 'beatmap_collections/snippets/beatmap_card_demo.html', {'beatmap': beatmap_detail})
        beatmap_card['Cache_Control'] = 'public, max_age=100000'
        beatmap_card['Vary'] = 'Accept-Encoding'
        return beatmap_card
    no_beatmap_response = """
    <div data-aos="fade-up" data-aos-duration="600" data-aos-once="true">
    <div class="alert alert-warning">
        <i class="fas fa-sad-cry" style="color: #664d03;"></i> No beatmap found! Beatto-chan is sad :(
    </div>
    </div>
    """
    return HttpResponse(no_beatmap_response, content_type='text/html')
