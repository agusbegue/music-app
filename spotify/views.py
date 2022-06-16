from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .interaction import *
from .models import User, SpotifyToken, UserProfile
from .auth import get_auth_url, request_spotify_token, user_is_authenticated

from .cron import get_data


class AuthURL(APIView):

    def get(self, request):
        return Response({'url': get_auth_url()}, status=status.HTTP_200_OK)


class GetData(APIView):

    def get(self, request):
        get_data()
        return Response('Process finished OK', status=status.HTTP_200_OK)


class SpotifyCallback(APIView):

    def get(self, request):
        code = request.GET.get('code')
        error = request.GET.get('error')
        if error or not code:
            return redirect('frontend:')

        token_data = request_spotify_token(code)
        if token_data.pop('error', False):
            return redirect('frontend:')

        if not request.session.exists(request.session.session_key):
            request.session.create()
        session_id = request.session.session_key

        user_data = get_spotify_user_data(access_token=token_data.get('access_token'))
        User.create_or_update_user(token_data=token_data, user_data=user_data, session_id=session_id)

        return redirect('frontend:')


class IsAuthenticated(APIView):

    def get(self, request):
        is_authenticated, _ = user_is_authenticated(request.session.session_key)
        return Response({'is_authenticated': is_authenticated}, status=status.HTTP_200_OK)


class Logout(APIView):

    def post(self, request):
        # print('Entered logout view')
        user = User.objects.get(session_id=request.session.session_key)
        user.logout()
        return Response({}, status=status.HTTP_200_OK)


# class PauseSong(APIView):
#     def put(self, response, format=None):
#         room_code = self.request.session.get('room_code')
#         room = Room.objects.filter(code=room_code)[0]
#         if self.request.session.session_key == room.host or room.guest_can_pause:
#             pause_song(room.host)
#             return Response({}, status=status.HTTP_204_NO_CONTENT)
#
#         return Response({}, status=status.HTTP_403_FORBIDDEN)
#
#
# class PlaySong(APIView):
#     def put(self, response, format=None):
#         room_code = self.request.session.get('room_code')
#         room = Room.objects.filter(code=room_code)[0]
#         if self.request.session.session_key == room.host or room.guest_can_pause:
#             play_song(room.host)
#             return Response({}, status=status.HTTP_204_NO_CONTENT)
#
#         return Response({}, status=status.HTTP_403_FORBIDDEN)
#
#
# class SkipSong(APIView):
#     def post(self, request, format=None):
#         room_code = self.request.session.get('room_code')
#         room = Room.objects.filter(code=room_code)[0]
#         votes = Vote.objects.filter(room=room, song_id=room.current_song)
#         votes_needed = room.votes_to_skip
#
#         if self.request.session.session_key == room.host or len(votes) + 1 >= votes_needed:
#             votes.delete()
#             skip_song(room.host)
#         else:
#             vote = Vote(user=self.request.session.session_key,
#                         room=room, song_id=room.current_song)
#             vote.save()
#
#         return Response({}, status.HTTP_204_NO_CONTENT)


# class CurrentSong(APIView):
#     def get(self, request, format=None):
#         room_code = self.request.session.get('room_code')
#         room = Room.objects.filter(code=room_code)
#         if room.exists():
#             room = room[0]
#         else:
#             return Response({}, status=status.HTTP_404_NOT_FOUND)
#         host = room.host
#         endpoint = "player/currently-playing"
#         response = execute_spotify_api_request(host, endpoint)
#
#         if 'error' in response or 'item' not in response:
#             return Response({}, status=status.HTTP_204_NO_CONTENT)
#
#         item = response.get('item')
#         duration = item.get('duration_ms')
#         progress = response.get('progress_ms')
#         album_cover = item.get('album').get('images')[0].get('url')
#         is_playing = response.get('is_playing')
#         song_id = item.get('id')
#
#         artist_string = ""
#
#         for i, artist in enumerate(item.get('artists')):
#             if i > 0:
#                 artist_string += ", "
#             name = artist.get('name')
#             artist_string += name
#
#         votes = len(Vote.objects.filter(room=room, song_id=song_id))
#         song = {
#             'title': item.get('name'),
#             'artist': artist_string,
#             'duration': duration,
#             'time': progress,
#             'image_url': album_cover,
#             'is_playing': is_playing,
#             'votes': votes,
#             'votes_required': room.votes_to_skip,
#             'id': song_id
#         }
#
#         self.update_room_song(room, song_id)
#
#         return Response(song, status=status.HTTP_200_OK)
#
#     def update_room_song(self, room, song_id):
#         current_song = room.current_song
#
#         if current_song != song_id:
#             room.current_song = song_id
#             room.save(update_fields=['current_song'])
#             votes = Vote.objects.filter(room=room).delete()


