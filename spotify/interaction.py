from .auth import get_user_access_token
from django.utils import timezone
from requests import post, put, get

BASE_URL = "https://api.spotify.com/v1/me/"


def execute_spotify_api_request(endpoint, access_token, request_type):

    headers = {'Content-Type': 'application/json',
               'Authorization': "Bearer " + access_token}
    if request_type == 'get':
        response = get(BASE_URL + endpoint, {}, headers=headers)
        try:
            return response.json()
        except:
            return {'Error': 'Issue with request'}
    elif request_type == 'put':
        put(BASE_URL + endpoint, headers=headers)
    elif request_type == 'post':
        post(BASE_URL + endpoint, headers=headers)
    else:
        raise NotImplemented(f'Request type: "{request_type}" not implemented')


def get_spotify_user_data(access_token):
    response = execute_spotify_api_request('', access_token, request_type='get')
    return {'name': response.get('display_name'), 'email': response.get('email'), 'user_id': response.get('id')}


def play_song(session_id):
    access_token = get_user_access_token(session_id)
    return execute_spotify_api_request("player/play", access_token, request_type='put')


def pause_song(session_id):
    access_token = get_user_access_token(session_id)
    return execute_spotify_api_request("player/pause", access_token, request_type='put')


def skip_song(session_id):
    access_token = get_user_access_token(session_id)
    return execute_spotify_api_request("player/next", access_token, request_type='post')
