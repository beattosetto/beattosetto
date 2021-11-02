import os
import time
import requests
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.db.models.functions import datetime
from django.utils import timezone

from actions.models import ActionLog
from beatmap_collections.models import Beatmap
from beattosetto.settings import OSU_API_V1_KEY
from django.utils.timezone import make_aware


def update_beatmap_action_script(action: ActionLog):
    """An action script for updating a beatmap's data entire server.

    Parameters:
        action (ActionLog): The ActionLog for tracking the action.
    """
    beatmap_count = Beatmap.objects.all().count()
    failed = 0
    success = 0
    count = 0
    for beatmap in Beatmap.objects.all():
        count += 1
        action.running_text = f"Updating {beatmap.title}[{beatmap.version}] ({count}/{beatmap_count})"
        action.save()
        beatmap_id = beatmap.beatmap_id
        parameter = {'b': beatmap.beatmap_id, 'k': OSU_API_V1_KEY}
        request_data = requests.get("https://osu.ppy.sh/api/get_beatmaps", params=parameter)
        if (request_data.status_code == 200) and (request_data.json() != []):
            try:
                beatmap_json = request_data.json()[0]

                action.running_text = f"Fetching the new beatmap picture of {beatmap.title} [{beatmap.version}] ({count}/{beatmap_count})"
                action.save()

                # Try to delete the old beatmap picture and replace it with a new one
                try:
                    os.remove(f"media/{beatmap.beatmap_card}")
                except FileNotFoundError:
                    pass

                try:
                    os.remove(f"media/{beatmap.beatmap_list}")
                except FileNotFoundError:
                    pass

                card_pic = requests.get(
                    f"https://assets.ppy.sh/beatmaps/{beatmap_json['beatmapset_id']}/covers/card.jpg")
                card_temp = NamedTemporaryFile(delete=True)
                card_temp.write(card_pic.content)
                card_temp.flush()
                beatmap.beatmap_card.save(f"{beatmap_id}.jpg", File(card_temp), save=True)

                list_pic = requests.get(
                    f"https://assets.ppy.sh/beatmaps/{beatmap_json['beatmapset_id']}/covers/list.jpg")
                list_temp = NamedTemporaryFile(delete=True)
                list_temp.write(list_pic.content)
                list_temp.flush()
                beatmap.beatmap_list.save(f"{beatmap_id}.jpg", File(list_temp), save=True)

                action.running_text = f"Updating the metadata of {beatmap.title} [{beatmap.version}] ({count}/{beatmap_count})"

                beatmap.beatmapset_id = beatmap_json['beatmapset_id']
                beatmap.title = beatmap_json['title']
                beatmap.artist = beatmap_json['artist']
                beatmap.source = beatmap_json['source']
                beatmap.creator = beatmap_json['creator']
                beatmap.approved = beatmap_json['approved']
                beatmap.difficultyrating = beatmap_json['difficultyrating']
                beatmap.bpm = beatmap_json['bpm']
                beatmap.version = beatmap_json['version']

                if beatmap_json['mode'] == '0':
                    beatmap.url = f"https://osu.ppy.sh/beatmapsets/{beatmap_json['beatmapset_id']}#osu/{beatmap_id}"
                elif beatmap_json['mode'] == '1':
                    beatmap.url = f"https://osu.ppy.sh/beatmapsets/{beatmap_json['beatmapset_id']}#taiko/{beatmap_id}"
                elif beatmap_json['mode'] == '2':
                    beatmap.url = f"https://osu.ppy.sh/beatmapsets/{beatmap_json['beatmapset_id']}#fruits/{beatmap_id}"
                elif beatmap_json['mode'] == '3':
                    beatmap.url = f"https://osu.ppy.sh/beatmapsets/{beatmap_json['beatmapset_id']}#mania/{beatmap_id}"
                else:
                    # This should never happen
                    beatmap.url = "https://osu.ppy.sh/"

                beatmap.count_normal = beatmap_json['count_normal']
                beatmap.count_slider = beatmap_json['count_slider']
                beatmap.count_spinner = beatmap_json['count_spinner']

                beatmap.diff_approach = beatmap_json['diff_approach']
                beatmap.diff_drain = beatmap_json['diff_drain']
                beatmap.diff_overall = beatmap_json['diff_overall']
                beatmap.diff_size = beatmap_json['diff_size']
                if beatmap_json['diff_aim'] is not None:
                    beatmap.diff_aim = beatmap_json['diff_aim']
                if beatmap_json['diff_speed'] is not None:
                    beatmap.diff_speed = beatmap_json['diff_speed']

                if beatmap_json['max_combo'] is not None:
                    beatmap.max_combo = beatmap_json['max_combo']
                beatmap.playcount = beatmap_json['playcount']
                beatmap.favourite_count = beatmap_json['favourite_count']
                beatmap.total_length = beatmap_json['total_length']
                beatmap.mode = beatmap_json['mode']
                beatmap.creator_id = beatmap_json['creator_id']
                beatmap.genre_id = beatmap_json['genre_id']
                beatmap.language_id = beatmap_json['language_id']
                beatmap.tags = beatmap_json['tags']

                beatmap.submit_date = make_aware(datetime.datetime.strptime(beatmap_json['submit_date'], '%Y-%m-%d %H:%M:%S'))
                if beatmap_json['approved_date'] is not None:
                    beatmap.approved_date = make_aware(datetime.datetime.strptime(beatmap_json['approved_date'], '%Y-%m-%d %H:%M:%S'))
                beatmap.last_update = make_aware(datetime.datetime.strptime(beatmap_json['last_update'], '%Y-%m-%d %H:%M:%S'))

                beatmap.save()
                success += 1
            except Exception as e:
                print(e)
                failed += 1
        else:
            failed += 1
        # To make the API request rate not too rush, we need to add a small delay on request
        time.sleep(5)
    action.status = 2
    action.running_text = f"Task running successfully with {success} success and {failed} failed!"
    action.time_finish = timezone.now()
    action.save()
