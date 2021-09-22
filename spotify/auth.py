from rest_framework.authentication import BaseAuthentication
from django.utils import timezone
from .models import SpotifyUser
from requests import post, Request
from datetime import timedelta


CLIENT_ID = "908d3e07450148849b073e188ba0216a"
CLIENT_SECRET = "d14f7cf76e734ba1b32e43b79f5e48cb"
REDIRECT_URI = "http://localhost:8001/spotify/redirect"

SCOPES = [
    'user-read-playback-state',
    'user-modify-playback-state',
    'user-read-currently-playing',
    'user-read-private',
    'user-read-email'
]


# class SpotifyAuthentication(BaseAuthentication):
#
#     def authenticate(self, request):
#         is_authenticated, user = user_is_authenticated(request.session.session_key)
#         if True:#is_authenticated:
#             return user, None
#         return None


def user_is_authenticated(session_id):
    user = SpotifyUser.objects.filter(session_id=session_id)
    if user.exists():
        return True, user[0]
    else:
        return False, None


def get_user_access_token(session_id):
    user = SpotifyUser.objects.filter(session_id=session_id)[0]
    if user.token_expiry <= timezone.now():
        refresh_spotify_token(user)
    return user.access_token


def get_auth_url():
    url = Request('GET', 'https://accounts.spotify.com/authorize', params={
        'scope': ' '.join(SCOPES),
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID
    }).prepare().url
    return url


def request_spotify_token(code):
    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }).json()

    return {
        'access_token': response.get('access_token'),
        'token_type': response.get('token_type'),
        'refresh_token': response.get('refresh_token'),
        'token_expiry': timezone.now() + timedelta(seconds=response.get('expires_in')),
        'error': response.get('error')
    }


def refresh_spotify_token(user):
    refresh_token = user.refresh_token

    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }).json()

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    token_expiry = timezone.now() + timedelta(seconds=response.get('expires_in'))

    user.update(access_token=access_token, token_type=token_type, token_expiry=token_expiry,
                refresh_token=refresh_token)



