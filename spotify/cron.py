import os
import logging

from spotify.models import Job, SpotifyToken, JobRun
from spotify.auth import get_user_access_token
from api.telegram import report
from api.models import (
    Artist, ArtistPopularity, Track, TrackRecord, Record, Playlist, ArtistBasic, TrackBasic
)
from spotify.interaction import (
    get_artists_data, get_playlists_data, get_tracks_popularity, get_artists_tracks
)
from musically.settings import BASE_DIR

# Logging
logger = logging.getLogger('scraper')
logging_dir = os.path.join(BASE_DIR, 'spotify/scraping/')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# To log debug messages
debug_log = logging.FileHandler(os.path.join(logging_dir, 'debug.log'))
debug_log.setLevel(logging.DEBUG)
debug_log.setFormatter(formatter)
logger.addHandler(debug_log)
# To log info messages
info_log = logging.FileHandler(os.path.join(logging_dir, 'info.log'))
info_log.setLevel(logging.INFO)
info_log.setFormatter(formatter)
logger.addHandler(info_log)

BATCH_SIZE = 500

DEBUG_MODE = True


def say_hello():
    logger.debug('Said hello')
    report('Reporting, all is good')


def get_data():
    job_name = 'scraping_job'
    report(f'Stating {job_name} job with DEBUG_MODE={DEBUG_MODE}')
    logger.debug(f'Starting {job_name} in mode: DEBUG={DEBUG_MODE}')

    # Check if scraping is turned on and we have access token
    access_token, job = get_token_object()
    if access_token:
        logger.debug('Found a job and an access token')

        # Get info from available playlists in the database
        playlists_obj = Playlist.objects.all()
        playlists_data = get_playlists_data(access_token, map(lambda p: p.id, playlists_obj))
        logger.debug(f'Retrieved {len(playlists_data)} playlists from database and extracted their data')

        # Save new artists in database
        saved_artists_obj = Artist.objects.all().values('id', 'name')
        saved_artist_ids = [artist.get('id') for artist in saved_artists_obj]
        p_artists_ids = set([artist['id'] for p_data in playlists_data.values() for track in p_data for artist in
                             track['track']['artists']])
        new_artists_ids = [artist_id for artist_id in p_artists_ids if artist_id not in saved_artist_ids]
        new_artists_data = get_artists_data(access_token, new_artists_ids)
        new_artists_obj = []
        for artist_data in new_artists_data.values():
            new_artists_obj.append(Artist.create_from_dict(**artist_data))
        if not DEBUG_MODE:
            try:
                Artist.objects.bulk_create(new_artists_obj, batch_size=BATCH_SIZE)
            except Exception as e:
                status = f'[scraper] - Error in inserting artists - {str(e)}'
                report(status)
                JobRun(name=job_name, status=status, debug=DEBUG_MODE).save()
                return
        logger.debug(f'Saved {len(new_artists_ids)} new artists in the database')

        # Get rest of the artists popularities
        old_artists_pop = get_artists_data(access_token, saved_artist_ids, just_popularity=True)
        logger.debug(f'Extracted popularity for {len(old_artists_pop)} existing artists')

        # Save all artists's popularities
        artist_pop_obj = []
        for old_artist in saved_artists_obj:
            artist_pop_obj.append(ArtistPopularity(artist=ArtistBasic.from_artist(old_artist),
                                                   popularity=old_artists_pop[old_artist.get('id')]['popularity']))
        for new_artist in new_artists_obj:
            artist_pop_obj.append(ArtistPopularity(artist=ArtistBasic.from_artist(new_artist),
                                                   popularity=new_artists_data[new_artist.get('id')]['popularity']))
        if not DEBUG_MODE:
            try:
                ArtistPopularity.objects.bulk_create(artist_pop_obj, batch_size=BATCH_SIZE)
            except Exception as e:
                status = f'[scraper] - Error in inserting artist popularities - {str(e)}'
                report(status)
                JobRun(name=job_name, status=status, debug=DEBUG_MODE).save()
                return
        logger.debug(f'Saved popularity for total of {len(artist_pop_obj)} artists')

        # Get all track in database
        saved_tracks = Track.objects.values('id', 'artists', 'name', 'relevant').iterator(chunk_size=2000)
        saved_tracks_ids = []
        relevant_tracks = {}
        for track in saved_tracks:
            saved_tracks_ids.append(track.get('id'))
            if track.get('relevant'):
                relevant_tracks[track.get('id')] = track
        logger.debug(f'Retrieved {len(saved_tracks_ids)} from database, {len(relevant_tracks)} relevant')

        # Get old artists new tracks
        old_artists_new_tracks = get_artists_tracks(access_token, saved_artist_ids, only_latest=True)
        old_artists_new_tracks = unpack_data(old_artists_new_tracks.values())
        logger.debug(f'Extracted {len(old_artists_new_tracks)} tracks from {len(saved_tracks_ids)} old artists')

        # Get new artists all tracks
        new_artists_tracks = get_artists_tracks(access_token, new_artists_ids, only_latest=False)
        new_artists_tracks = unpack_data(new_artists_tracks.values())
        logger.debug(f'Extracted {len(new_artists_tracks)} tracks from {len(new_artists_ids)} new artists')

        # Filter out tracks already present
        new_tracks_data = {track['id']: track for track in list(filter(
            lambda f: f['id'] not in saved_tracks_ids, old_artists_new_tracks + new_artists_tracks))}
        logger.debug(f'Filtered {len(old_artists_new_tracks+new_artists_tracks)-len(new_tracks_data)} repeated tracks')

        # Get all ranking records
        rank_records = {}
        for playlist in playlists_obj:
            for rank, track in enumerate(playlists_data[playlist.id], 1):
                record = Record.from_playlist(playlist_code=playlist.code, rank=rank)
                if track['track']['id'] not in rank_records:
                    rank_records[track['track']['id']] = []
                rank_records[track['track']['id']].append(record)
        logger.debug(f'Processed ranking records for {len(rank_records)} tracks')

        # Save new tracks in database
        new_tracks_obj = []
        for track_id, track_data in new_tracks_data.items():
            relevant = track_id in rank_records
            track = Track.create_from_dict(**track_data, **{'relevant': relevant})
            new_tracks_obj.append(track)
            if relevant:
                relevant_tracks[track_id] = track
        if not DEBUG_MODE:
            try:
                Track.objects.bulk_create(new_tracks_obj, batch_size=BATCH_SIZE)
            except Exception as e:
                status = f'[scraper] - Error in inserting tracks - {str(e)}'
                report(status)
                JobRun(name=job_name, status=status, debug=DEBUG_MODE).save()
                return
        logger.debug(f'Saved {len(new_tracks_obj)} tracks in database')

        # Update new relevant tracks in database
        Track.objects.filter(relevant__in=[False], id__in=list(rank_records.keys())).update(relevant=True)

        # Get all relevant track's popularity
        track_popularities = get_tracks_popularity(access_token, list(relevant_tracks.keys()))
        logger.debug(f'Extracted popularity for {len(track_popularities)} tracks')

        # Save track popularities and rankings
        track_records = []
        for track_id, track in relevant_tracks.items():
            records = [Record.from_popularity(popularity=track_popularities[track_id])]
            if track_id in rank_records:
                records.extend(rank_records[track_id])
            track_records.append(TrackRecord(track=TrackBasic.from_track(track), records=records))
        if not DEBUG_MODE:
            try:
                TrackRecord.objects.bulk_create(track_records, batch_size=BATCH_SIZE)
            except Exception as e:
                status = f'[scraper] - Error in inserting track records - {str(e)}'
                report(status)
                JobRun(name=job_name, status=status, debug=DEBUG_MODE).save()
                return
        logger.debug(f'Saved records for {len(track_records)} tracks')

        summary_message = [
            f'Sraping summary: done successfully in DEBUG_MODE={DEBUG_MODE}',
            f'- Extracted data from {len(playlists_data)} playlists',
            f'- Added {len(new_artists_data)} new artists, totalizing {len(new_artists_ids + saved_artist_ids)}',
            f'- Extended {len(artist_pop_obj)} artist popularity objects',
            f'- Added {len(new_tracks_obj)} new tracks, totalizing {len(new_tracks_data) + len(saved_tracks_ids)}',
            f'- Extended {len(track_records)} track record objects',
        ]

    else:
        summary_message = ['Scraping summary: no job or token found']

    JobRun(name=job_name, status=summary_message[0], debug=DEBUG_MODE).save()
    for line in summary_message:
        logger.info(line)
        report(line)


def get_token_object():
    try:
        for job in Job.objects.filter(active__in=[True]):
            try:
                return get_user_access_token(user_id=job.user_id), job
            except SpotifyToken.DoesNotExist:
                pass
        return None, None
    except Exception as e:
        logger.debug(str(e))


def unpack_data(data):
    return [item for group in data for item in group]

