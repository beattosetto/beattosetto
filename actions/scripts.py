"""
Script for using in worker.
"""
import logging
import os
import time
import requests
import traceback
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.db.models.functions import datetime
from django.utils import timezone
from .logging import setup_logger, log_two_handler, LOG_FORMAT, LOG_DEBUG_FORMAT
from .models import ActionLog
from beatmap_collections.models import Beatmap
from beattosetto.settings import OSU_API_V1_KEY
from django.utils.timezone import make_aware


def update_beatmap_action_script(action: ActionLog):
    """An action script for updating a beatmap's data entire server.

    Parameters:
        action (ActionLog): The ActionLog for tracking the action.
    """
    try:
        # For running first time, make a new folder for store debug log
        if not os.path.exists('actions_logs_debug'):
            os.mkdir('actions_logs_debug')
        # Setup the new logger
        info_logger = setup_logger(f'info_log_{action.id}', f'media/{action.log}', 'a+', logging.INFO, LOG_FORMAT)
        debug_logger = setup_logger(f'debug_log_{action.id}', f'actions_logs_debug/log_{action.id}_debug.log',
                                    'a+', logging.DEBUG, LOG_DEBUG_FORMAT)
        log_two_handler(info_logger, debug_logger, logging.INFO, "Setup logger complete.")
        beatmap_count = Beatmap.objects.all().count()
        log_two_handler(info_logger, debug_logger, logging.INFO, f"Prepare to update {beatmap_count} beatmaps.")
        failed = 0
        success = 0
        count = 0
        for beatmap in Beatmap.objects.all():
            count += 1
            action.running_text = f"Updating {beatmap.title}[{beatmap.version}] ({count}/{beatmap_count})"
            action.save()
            log_two_handler(info_logger, debug_logger, logging.INFO,
                            f"Updating {beatmap.title}[{beatmap.version}] ({count}/{beatmap_count})")
            beatmap_id = beatmap.beatmap_id
            parameter = {'b': beatmap.beatmap_id, 'k': OSU_API_V1_KEY}
            log_two_handler(info_logger, debug_logger, logging.INFO,
                            f'Requesting beatmap data for {beatmap.title}[{beatmap.version}] ({count}/{beatmap_count})')
            request_data = requests.get("https://osu.ppy.sh/api/get_beatmaps", params=parameter)
            if (request_data.status_code == 200) and (request_data.json() != []):
                try:
                    beatmap_json = request_data.json()[0]
                    log_two_handler(info_logger, debug_logger, logging.INFO,
                                    f'Beatmap data received for {beatmap.title}[{beatmap.version}]')
                    debug_logger.debug(f"{beatmap.title}[{beatmap.version}] JSON Data : {beatmap_json}")

                    action.running_text = f"Fetching the new beatmap picture of" \
                                          f" {beatmap.title}[{beatmap.version}] ({count}/{beatmap_count})"
                    action.save()

                    # Try to delete the old beatmap picture and replace it with a new one
                    # But first, check that beatmap is not use the default picture
                    if beatmap.beatmap_card != "default_beatmap_cover.png" and beatmap.beatmap_card != "default_beatmap_cover.jpg":
                        try:
                            os.remove(f"media/{beatmap.beatmap_card}")
                            log_two_handler(info_logger, debug_logger, logging.INFO,
                                            f"Deleted old beatmap card picture of {beatmap.title}[{beatmap.version}]")
                        except FileNotFoundError:
                            log_two_handler(info_logger, debug_logger, logging.WARNING,
                                            f"No old beatmap card picture of {beatmap.title}[{beatmap.version}] to delete, pass it.")
                    else:
                        log_two_handler(info_logger, debug_logger, logging.INFO,
                                        f"{beatmap.title}[{beatmap.version}] use default beatmap card picture, pass it.")

                    if beatmap.beatmap_list != "default_beatmap_thumbnail.png" and beatmap.beatmap_list != "default_beatmap_thumbnail.jpg":
                        try:
                            os.remove(f"media/{beatmap.beatmap_list}")
                            log_two_handler(info_logger, debug_logger, logging.INFO,
                                            f"Deleted old beatmap list picture of {beatmap.title}[{beatmap.version}]")
                        except FileNotFoundError:
                            log_two_handler(info_logger, debug_logger, logging.WARNING,
                                            f"No old beatmap list picture of {beatmap.title}[{beatmap.version}] to delete, pass it.")
                    else:
                        log_two_handler(info_logger, debug_logger, logging.INFO,
                                        f"{beatmap.title}[{beatmap.version}] use default beatmap list picture, pass it.")

                    card_pic = requests.get(
                        f"https://assets.ppy.sh/beatmaps/{beatmap_json['beatmapset_id']}/covers/card.jpg")
                    debug_logger.info(f"Content of {beatmap.title}[{beatmap.version}] beatmap card picture :\n{str(card_pic.content)}")
                    if "Access Denied" not in str(card_pic.content):
                        card_temp = NamedTemporaryFile(delete=True)
                        card_temp.write(card_pic.content)
                        card_temp.flush()
                        beatmap.beatmap_card.save(f"{beatmap_id}.jpg", File(card_temp), save=True)
                        card_temp.close()
                        log_two_handler(info_logger, debug_logger, logging.INFO,
                                        f"Saved new beatmap card picture of {beatmap.title}[{beatmap.version}]")
                    else:
                        log_two_handler(info_logger, debug_logger, logging.WARNING,
                                        f"Beatmap card picture of {beatmap.title}[{beatmap.version}] not found, skipping.")

                    list_pic = requests.get(
                        f"https://assets.ppy.sh/beatmaps/{beatmap_json['beatmapset_id']}/covers/list.jpg")
                    debug_logger.info(f"Content of {beatmap.title}[{beatmap.version}] beatmap list picture : \n{str(list_pic.content)}")
                    if "Access Denied" not in str(list_pic.content):
                        list_temp = NamedTemporaryFile(delete=True)
                        list_temp.write(list_pic.content)
                        list_temp.flush()
                        beatmap.beatmap_list.save(f"{beatmap_id}.jpg", File(list_temp), save=True)
                        list_temp.close()
                        log_two_handler(info_logger, debug_logger, logging.INFO,
                                        f"Saved new beatmap list picture of {beatmap.title}[{beatmap.version}]")
                    else:
                        log_two_handler(info_logger, debug_logger, logging.WARNING,
                                        f"Beatmap list picture of {beatmap.title}[{beatmap.version}] not found, skipping.")

                    action.running_text = f"Updating the URL of {beatmap.title}[{beatmap.version}] ({count}/{beatmap_count})"
                    log_two_handler(info_logger, debug_logger, logging.INFO,
                                    f"Updating the URL of {beatmap.title} [{beatmap.version}]")

                    if beatmap_json['mode'] == '0':
                        beatmap.url = f"https://osu.ppy.sh/beatmapsets/{beatmap_json['beatmapset_id']}#osu/{beatmap_id}"
                        beatmap.save()
                    elif beatmap_json['mode'] == '1':
                        beatmap.url = f"https://osu.ppy.sh/beatmapsets/{beatmap_json['beatmapset_id']}#taiko/{beatmap_id}"
                        beatmap.save()
                    elif beatmap_json['mode'] == '2':
                        beatmap.url = f"https://osu.ppy.sh/beatmapsets/{beatmap_json['beatmapset_id']}#fruits/{beatmap_id}"
                        beatmap.save()
                    elif beatmap_json['mode'] == '3':
                        beatmap.url = f"https://osu.ppy.sh/beatmapsets/{beatmap_json['beatmapset_id']}#mania/{beatmap_id}"
                        beatmap.save()
                    else:
                        # This should never happen
                        beatmap.url = "https://osu.ppy.sh/"

                    action.running_text = f"Updating the metadata of {beatmap.title}[{beatmap.version}] ({count}/{beatmap_count})"
                    log_two_handler(info_logger, debug_logger, logging.INFO, f"Updating the metadata of {beatmap.title} [{beatmap.version}]")

                    beatmap.beatmapset_id = beatmap_json['beatmapset_id']
                    beatmap.title = beatmap_json['title']
                    beatmap.artist = beatmap_json['artist']
                    beatmap.source = beatmap_json['source']
                    beatmap.creator = beatmap_json['creator']

                    beatmap.approved = beatmap_json['approved']
                    beatmap.difficultyrating = beatmap_json['difficultyrating']
                    beatmap.bpm = beatmap_json['bpm']
                    beatmap.version = beatmap_json['version']

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
                    beatmap.genre_id = beatmap_json['genre_id']
                    beatmap.language_id = beatmap_json['language_id']
                    beatmap.tags = beatmap_json['tags']

                    beatmap.submit_date = make_aware(datetime.datetime.strptime(beatmap_json['submit_date'], '%Y-%m-%d %H:%M:%S'))
                    if beatmap_json['approved_date'] is not None:
                        beatmap.approved_date = make_aware(datetime.datetime.strptime(beatmap_json['approved_date'], '%Y-%m-%d %H:%M:%S'))
                    beatmap.last_update = make_aware(datetime.datetime.strptime(beatmap_json['last_update'], '%Y-%m-%d %H:%M:%S'))

                    beatmap.save()
                    log_two_handler(info_logger, debug_logger, logging.INFO,
                                    f"Saved new metadata of {beatmap.title}[{beatmap.version}]")
                    success += 1
                except Exception as error:
                    log_two_handler(info_logger, debug_logger, logging.ERROR,
                                    f"Error while updating the metadata of {beatmap.title}[{beatmap.version}] : {str(error)}")
                    log_two_handler(info_logger, debug_logger, logging.ERROR, f"Traceback detail: \n {traceback.format_exc()}")
                    failed += 1
            else:
                log_two_handler(info_logger, debug_logger, logging.ERROR,
                                f"Failed to fetch beatmap data of {beatmap.title}[{beatmap.version}] from osu! API")
                debug_logger.error(f"Status Code: {request_data.status_code}")
                debug_logger.error(f"JSON Data: {request_data.json()}")
                failed += 1
            # To make the API request rate not too rush, we need to add a small delay on request
            time.sleep(5)
        action.status = 2
        action.running_text = f"Task running successfully with {success} success and {failed} failed!"
        action.time_finish = timezone.now()
        action.save()
        log_two_handler(info_logger, debug_logger, logging.INFO,
                        f"Task running successfully with {success} success and {failed} failed!")
        log_two_handler(info_logger, debug_logger, logging.INFO, "Action finished! Thanks for using beatto-chan services.")
    except Exception as error:
        action.status = 3
        action.running_text = f"Start Action failed : {str(error)}"
        action.time_finish = timezone.now()
        action.save()
