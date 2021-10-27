from django import template
from beatmap_collections.models import BeatmapEntry

register = template.Library()


def count_beatmaps(collection):
    beatmap_count = BeatmapEntry.objects.filter(collection=collection).count()
    if beatmap_count == 0:
        return "0 beatmap"
    else:
        return str(beatmap_count) + " beatmaps"


register.filter('count_beatmaps', count_beatmaps)
