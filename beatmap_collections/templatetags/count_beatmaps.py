from django import template
from beatmap_collections.models import BeatmapEntry

register = template.Library()


def count_beatmaps(collection):
    """A snippets that count the BeatmapEntry that is in the collection.

    Args:
        collection (Collection): The collection that you want to count.

    Returns:
        int: The number of beatmaps in the collection.
    """
    beatmap_count = BeatmapEntry.objects.filter(collection=collection).count()
    if beatmap_count == 0 or beatmap_count == 1:
        return str(beatmap_count) + " beatmap"
    return str(beatmap_count) + " beatmaps"


register.filter('count_beatmaps', count_beatmaps)
