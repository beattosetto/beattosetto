"""
This file use to create beatmap from beatmap id.
"""
import requests
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.db.models.functions import datetime
from beatmap_collections.models import Beatmap
from beattosetto.settings import OSU_API_V1_KEY
from django.utils.timezone import make_aware


def create_beatmap(beatmap_id):
    """
    Creates a Beatmap object from beatmap ID.

    Parameters:
        beatmap_id (int): Beatmap ID.

    Returns:
        Beatmap object.
    """
    parameter = {'b': beatmap_id, 'k': OSU_API_V1_KEY}
    request_data = requests.get("https://osu.ppy.sh/api/get_beatmaps", params=parameter)
    if (request_data.status_code == 200) and (request_data.json() != []):
        try:
            beatmap_json = request_data.json()[0]
            beatmap_object = Beatmap.objects.create()

            beatmap_object.beatmap_id = beatmap_json['beatmap_id']
            beatmap_object.beatmapset_id = beatmap_json['beatmapset_id']
            beatmap_object.title = beatmap_json['title']
            beatmap_object.artist = beatmap_json['artist']
            beatmap_object.source = beatmap_json['source']
            beatmap_object.creator = beatmap_json['creator']
            beatmap_object.approved = beatmap_json['approved']
            beatmap_object.difficultyrating = beatmap_json['difficultyrating']
            beatmap_object.bpm = beatmap_json['bpm']
            beatmap_object.version = beatmap_json['version']

            if beatmap_json['mode'] == '0':
                beatmap_object.URL = f"https://osu.ppy.sh/beatmapsets/{beatmap_json['beatmapset_id']}#osu/{beatmap_id}"
            elif beatmap_json['mode'] == '1':
                beatmap_object.URL = f"https://osu.ppy.sh/beatmapsets/{beatmap_json['beatmapset_id']}#taiko/{beatmap_id}"
            elif beatmap_json['mode'] == '2':
                beatmap_object.URL = f"https://osu.ppy.sh/beatmapsets/{beatmap_json['beatmapset_id']}#fruits/{beatmap_id}"
            elif beatmap_json['mode'] == '3':
                beatmap_object.URL = f"https://osu.ppy.sh/beatmapsets/{beatmap_json['beatmapset_id']}#mania/{beatmap_id}"
            else:
                # This should never happen
                beatmap_object.URL = "https://osu.ppy.sh/"

            # Download beatmap cover from osu! server and save it to the media storage and put the address in the model
            card_pic = requests.get(
                f"https://assets.ppy.sh/beatmaps/{beatmap_json['beatmapset_id']}/covers/card.jpg")
            # Check that beatmap card picture is exist
            if "Access Denied" not in str(card_pic.content):
                card_temp = NamedTemporaryFile(delete=True)
                card_temp.write(card_pic.content)
                card_temp.flush()
                beatmap_object.beatmap_card.save(f"{beatmap_id}.jpg", File(card_temp), save=True)

            list_pic = requests.get(
                f"https://assets.ppy.sh/beatmaps/{beatmap_json['beatmapset_id']}/covers/list.jpg")
            # Check that beatmap list picture is exist
            if "Access Denied" not in str(card_pic.content):
                list_temp = NamedTemporaryFile(delete=True)
                list_temp.write(list_pic.content)
                list_temp.flush()
                beatmap_object.beatmap_list.save(f"{beatmap_id}.jpg", File(list_temp), save=True)

            beatmap_object.count_normal = beatmap_json['count_normal']
            beatmap_object.count_slider = beatmap_json['count_slider']
            beatmap_object.count_spinner = beatmap_json['count_spinner']

            beatmap_object.diff_approach = beatmap_json['diff_approach']
            beatmap_object.diff_drain = beatmap_json['diff_drain']
            beatmap_object.diff_overall = beatmap_json['diff_overall']
            beatmap_object.diff_size = beatmap_json['diff_size']
            if beatmap_json['diff_aim'] is not None:
                beatmap_object.diff_aim = beatmap_json['diff_aim']
            if beatmap_json['diff_speed'] is not None:
                beatmap_object.diff_speed = beatmap_json['diff_speed']

            if beatmap_json['max_combo'] is not None:
                beatmap_object.max_combo = beatmap_json['max_combo']
            beatmap_object.playcount = beatmap_json['playcount']
            beatmap_object.favourite_count = beatmap_json['favourite_count']
            beatmap_object.total_length = beatmap_json['total_length']
            beatmap_object.mode = beatmap_json['mode']
            beatmap_object.creator_id = beatmap_json['creator_id']
            beatmap_object.genre_id = beatmap_json['genre_id']
            beatmap_object.language_id = beatmap_json['language_id']
            beatmap_object.tags = beatmap_json['tags']

            beatmap_object.submit_date = make_aware(
                datetime.datetime.strptime(beatmap_json['submit_date'], '%Y-%m-%d %H:%M:%S'))
            if beatmap_json['approved_date'] is not None:
                beatmap_object.approved_date = make_aware(
                    datetime.datetime.strptime(beatmap_json['approved_date'], '%Y-%m-%d %H:%M:%S'))
            beatmap_object.last_update = make_aware(
                datetime.datetime.strptime(beatmap_json['last_update'], '%Y-%m-%d %H:%M:%S'))

            beatmap_object.save()
            return beatmap_object
        except Exception as exception:
            print(exception)
            return None
    else:
        return None


def get_beatmap_detail(beatmap_id: int) -> dict:
    """
    Return a dictionary list of beatmap detail from API

    Args:
        beatmap_id (int) : The beatmap ID that want information

    Returns:
        dict : The beatmap detail
    """
    parameter = {'b': beatmap_id, 'k': OSU_API_V1_KEY}
    request_data = requests.get("https://osu.ppy.sh/api/get_beatmaps", params=parameter)
    if (request_data.status_code == 200) and (request_data.json() != []):
        return request_data.json()[0]
    return None
