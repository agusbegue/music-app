import os
import yaml
from requests import post, Request
from datetime import timedelta

from django.utils import timezone
from rest_framework.authentication import BaseAuthentication

from .settings import REDIRECT_URI, SCOPES
from .models import User, SpotifyToken
from music_app.settings import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET


class SpotifyAuthentication(BaseAuthentication):

    def authenticate(self, request):
        is_authenticated, user = user_is_authenticated(request.session.session_key)
        if is_authenticated:
            return user, None
        return None


def user_is_authenticated(session_id):
    user = User.objects.filter(session_id=session_id)
    if user.exists():
        return True, user[0]
    else:
        return False, None


def get_user_access_token(session_id=None, user_id=None):
    if session_id:
        token_object = SpotifyToken.objects.get(user__session_id=session_id)
    elif user_id:
        token_object = SpotifyToken.objects.get(user_id=user_id)
    else:
        raise ValueError('No session id or user id provided')
    if token_object.token_expiry <= timezone.now():
        refresh_spotify_token(token_object)
    return token_object.access_token


def get_auth_url():
    url = Request('GET', 'https://accounts.spotify.com/authorize', params={
        'scope': ' '.join(SCOPES),
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'client_id': SPOTIFY_CLIENT_ID
    }).prepare().url
    return url


def request_spotify_token(code):
    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET
    }).json()
    return {
        'access_token': response['access_token'],
        'token_type': response['token_type'],
        'refresh_token': response['refresh_token'],
        'token_expiry': timezone.now() + timedelta(seconds=response['expires_in']),
        'error': response.get('error')
    }


def refresh_spotify_token(token_object):
    refresh_token = token_object.refresh_token
    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET
    }).json()
    token_object.access_token = response['access_token']
    token_object.token_type = response['token_type']
    token_object.token_expiry = timezone.now() + timedelta(seconds=response['expires_in'])
    token_object.save()



