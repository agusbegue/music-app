from datetime import date, timedelta
from django.utils import timezone
from requests import post, put, get

from .settings import API_BASE_URL
from api.models import Artist, Track
from api.telegram import report


def execute_spotify_api_request(endpoint, access_token, request_type, query_params={}, key=None):

    headers = {'Content-Type': 'application/json',
               'Authorization': "Bearer " + access_token}
    url = API_BASE_URL + endpoint

    if request_type == 'get':
        if query_params:
            url += '?'
            for k, v in query_params.items():
                if isinstance(v, list):
                    url += k + '=' + '%2C'.join(v) + '&'
                else:
                    url += k + '=' + str(v) + '&'
            url = url[:-1]

        response = get(url, query_params, headers=headers)
        try:
            if key:
                return response.json()[key]
            else:
                return response.json()
        except Exception as e:
            report(f'[scraper] - Error in request to spotify - {str(e)}')
            return
    elif request_type == 'put':
        put(url, headers=headers)
    elif request_type == 'post':
        post(url, headers=headers)
    else:
        raise NotImplemented(f'Request type: "{request_type}" not implemented')


def get_spotify_user_data(access_token):
    response = execute_spotify_api_request('me', access_token, request_type='get')
    return {'name': response.get('display_name'),
            'email': response.get('email'),
            'user_id': response.get('id'),
            'country': response.get('country')}


def get_playlists_data(access_token, playlist_ids):
    playlists = {}
    for p_id in playlist_ids:
        playlists[p_id] = execute_spotify_api_request(
            f'playlists/{p_id}/tracks', access_token, 'get', key='items'
        )
    return playlists


def get_playlists_data_v2(access_token, playlists_ids, batch_size=100):
    playlists = {}
    for p_id in playlists_ids:
        playlists[p_id] = []
        i = 0
        total = 1
        while i < total:
            raw_data = execute_spotify_api_request(
                f'playlists/{p_id}/tracks', access_token, 'get',
                {'limit': batch_size, 'offset': i, 'fields': 'total,items(added_at,track.id)'}
            )
            playlists[p_id].extend(list(map(lambda f: {
                'track_id': f['track']['id'], 'added_at': f['added_at'], 'popularity': f['track']['popularity']
            }, raw_data['items'])))
            total = raw_data['total']
            i += batch_size
    return playlists


def get_tracks_audio_features(access_token, track_ids, batch_size=40):
    features = [
        'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness',
        'liveness', 'valence', 'tempo', 'duration_ms'
    ]
    audio_features = {}
    for i in range(0, len(track_ids), batch_size):
        raw_data = execute_spotify_api_request(
            'audio-features', access_token, 'get', {'ids': track_ids[i:min(i+batch_size, len(track_ids))]},
            key='audio_features'
        )
        audio_features.update({t['id']: {k: v for k, v in t.items() if k in features} for t in raw_data if t})
    return audio_features


def get_tracks_popularity(access_token, track_ids, batch_size=40):
    popularities = {}
    for i in range(0, len(track_ids), batch_size):
        raw_data = execute_spotify_api_request(
            'tracks', access_token, 'get', {'ids': track_ids[i:min(i+batch_size, len(track_ids))]},
            key='tracks'
        )
        popularities.update({t['id']: t['popularity'] for t in raw_data})
    return popularities


def get_artists_data(access_token, artist_ids, batch_size=20, just_popularity=False):
    fields = Artist.get_fields()+['popularity'] if not just_popularity else ['id', 'popularity']
    artist_data = {}
    for i in range(0, len(artist_ids), batch_size):
        raw_data = execute_spotify_api_request(
            'artists', access_token, 'get', {'ids': artist_ids[i:min(i+batch_size, len(artist_ids))]},
            key='artists'
        )
        artist_data.update({a['id']: {f: a[f] for f in a.keys() if f in fields} for a in raw_data})
    return artist_data


def get_artists_tracks(access_token, artist_ids, only_latest=False):
    num_tracks = 5 if only_latest else 50
    artists_tracks = {}
    for artist_id in artist_ids:
        raw_data = execute_spotify_api_request(
            f'artists/{artist_id}/albums?limit={num_tracks}&include_groups=single,album', access_token, 'get',
            key='items'
        )
        raw_data = list(filter(
            lambda f: f['release_date_precision'] == 'day' and
                      date(*map(int, f['release_date'].split('-'))) >= timezone.now().date()-timedelta(days=2), raw_data
        )) if only_latest else raw_data
        albums_tracks = get_album_tracks(access_token, list(map(lambda f: f['id'], raw_data)))
        artists_tracks.update({artist_id: [{field: t.get(field) for field in Track.get_fields()} for t in albums_tracks]})
    return artists_tracks


def get_album_tracks(access_token, album_ids, batch_size=10):
    if len(album_ids) == 0:
        return []
    albums_tracks = []
    for i in range(0, len(album_ids), batch_size):
        raw_data = execute_spotify_api_request(
            'albums', access_token, 'get', {'ids': album_ids[i:min(i+batch_size, len(album_ids))]},
            key='albums'
        )
        for album in raw_data:
            album_tracks = [dict(track, images=album['images']) for album in raw_data for track in album['tracks']['items']]
            if album['album_type'] == 'single':
                album_tracks = list(map(lambda f: dict(f, release_date=album['release_date']), album_tracks))
            albums_tracks.extend(album_tracks)
    return albums_tracks


def get_user_playlists(access_token, owner_id=None, min_tracks=None, batch_size=50):
    playlists = []
    i = 0
    total = 1
    while i < total:
        raw_data = execute_spotify_api_request(f'me/playlists', access_token, 'get', {'limit': batch_size, 'offset': i})
        playlists.extend(list(map(lambda f: {
            'name': f['name'], 'id': f['id'], 'owner_id': f['owner']['id'], 'tracks': f['tracks']['total']
        }, raw_data['items'])))
        total = raw_data['total']
        i += batch_size
    if owner_id:
        playlists = list(filter(lambda f: f['owner_id'] == owner_id, playlists))
    if min_tracks is not None:
        playlists = list(filter(lambda f: f['tracks'] >= min_tracks, playlists))
    return list(map(lambda f: {k: f[k] for k in ['name', 'id']}, playlists))


def get_user_top_tracks(access_token, time_range, num_tracks=50, batch_size=50):
    data = []
    for i in range(0, num_tracks, batch_size):
        batch_data = execute_spotify_api_request(
            'me/top/tracks', access_token, 'get',
            {'time_range': time_range, 'offset': i, 'limit': min(batch_size, num_tracks-i)},
            key='items'
        )
        batch_data = list(map(lambda f: {
            'name': f['name'], 'artists': list(map(lambda a: a['name'], f['artists']))
        }, batch_data))
        data.extend(batch_data)
    return data


def get_user_top_artists(access_token, time_range, num_artists=50, batch_size=50):
    data = []
    for i in range(0, num_artists, batch_size):
        batch_data = execute_spotify_api_request(
            'me/top/artists', access_token, 'get',
            {'time_range': time_range, 'offset': i, 'limit': min(batch_size, num_artists-i)},
            key='items'
        )
        batch_data = list(map(lambda f: {'name': f['name']}, batch_data))
        data.extend(batch_data)
    return data



# def play_song(session_id):
#     access_token = get_user_access_token(session_id)
#     return execute_spotify_api_request("/me/player/play", access_token, request_type='put')
#
#
# def pause_song(session_id):
#     access_token = get_user_access_token(session_id)
#     return execute_spotify_api_request("/me/player/pause", access_token, request_type='put')
#
#
# def skip_song(session_id):
#     access_token = get_user_access_token(session_id)
#     return execute_spotify_api_request("/me/player/next", access_token, request_type='post')
