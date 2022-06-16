import random
import numpy as np

from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from spotify.auth import SpotifyAuthentication, get_user_access_token, user_is_authenticated
from spotify.interaction import (
    get_user_top_tracks, get_user_top_artists, get_user_playlists, get_playlists_data_v2, get_tracks_audio_features
)


class GetTopTracksView(APIView):
    authentication_classes = [SpotifyAuthentication]

    def get(self, request, format=None):
        access_token = get_user_access_token(session_id=request.session.session_key)
        top_tracks = get_user_top_tracks(
            access_token,
            time_range=request.GET.get('time_range'),
            num_tracks=int(request.GET.get('amount'))
        )
        top_tracks_str = list(map(lambda f: f['name']+' - '+', '.join(f['artists']), top_tracks))
        return Response(top_tracks_str, status=status.HTTP_200_OK)


class GetTopArtistsView(APIView):
    authentication_classes = [SpotifyAuthentication]

    def get(self, request, format=None):
        access_token = get_user_access_token(session_id=request.session.session_key)
        top_artists = get_user_top_artists(
            access_token,
            time_range=request.GET.get('time_range'),
            num_artists=int(request.GET.get('amount')),
        )
        top_artists_str = list(map(lambda f: f['name'], top_artists))
        return Response(top_artists_str, status=status.HTTP_200_OK)


class GetUserPlaylists(APIView):
    authentication_classes = [SpotifyAuthentication]

    def get(self, request, format=None):
        access_token = get_user_access_token(session_id=request.session.session_key)
        auth, user = user_is_authenticated(session_id=request.session.session_key)
        playlists = get_user_playlists(access_token, owner_id=user.id)
        return Response(playlists, status=status.HTTP_200_OK)


class GetPlaylistAnalysisBoxplot(APIView):
    authentication_classes = [SpotifyAuthentication]
    features = [
        'danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness',
        'valence', 'tempo'
    ]

    def get(self, request, playlist_id):
        access_token = get_user_access_token(session_id=request.session.session_key)
        playlist_data = get_playlists_data_v2(access_token, [playlist_id])[playlist_id]
        tracks_features = get_tracks_audio_features(
            access_token, random.sample(list(map(lambda f: f['track_id'], playlist_data)), 30), batch_size=30
        )
        popularities = {t['track_id']: t['popularity'] for t in tracks_features}
        tracks_features = list(map(lambda f: {**f, 'popularity': popularities[f['track_id']]}, tracks_features))

        tracks_features = list(map(lambda f: {}))
        tracks_features = list(map(lambda f: {k: f[k] for k in self.features+['id', 'name']}, tracks_features))
        return Response(tracks_features, status=status.HTTP_200_OK)

    def get_boxplot_data(self, data):
        data = np.array(data)
        quartile1 = np.percentile(data, 25)
        quartile3 = np.percentile(data, 75)
        iqr = quartile3 - quartile1
        return {
            'whiskerLow': data[data >= quartile1 - 1.5 * iqr].min(),
            'quartile1': quartile1,
            'quartile2': np.median(data),
            'quartile3': quartile3,
            'whiskerHigh': data[data >= quartile1 + 1.5 * iqr].max()
        }

# class ArtistsView(generics.ListAPIView):


# class RoomView(generics.ListAPIView):
#     queryset = Room.objects.all()
#     serializer_class = RoomSerializer
#
#
# class GetRoom(APIView):
#     serializer_class = RoomSerializer
#     lookup_url_kwarg = 'code'
#
#     def get(self, request, format=None):
#         code = request.GET.get(self.lookup_url_kwarg)
#         if code != None:
#             room = Room.objects.filter(code=code)
#             if len(room) > 0:
#                 data = RoomSerializer(room[0]).data
#                 data['is_host'] = self.request.session.session_key == room[0].host
#                 return Response(data, status=status.HTTP_200_OK)
#             return Response({'Room Not Found': 'Invalid Room Code.'}, status=status.HTTP_404_NOT_FOUND)
#
#         return Response({'Bad Request': 'Code paramater not found in request'}, status=status.HTTP_400_BAD_REQUEST)
#
#
# class JoinRoom(APIView):
#     lookup_url_kwarg = 'code'
#
#     def post(self, request, format=None):
#         if not self.request.session.exists(self.request.session.session_key):
#             self.request.session.create()
#
#         code = request.data.get(self.lookup_url_kwarg)
#         if code != None:
#             room_result = Room.objects.filter(code=code)
#             if len(room_result) > 0:
#                 room = room_result[0]
#                 self.request.session['room_code'] = code
#                 return Response({'message': 'Room Joined!'}, status=status.HTTP_200_OK)
#
#             return Response({'Bad Request': 'Invalid Room Code'}, status=status.HTTP_400_BAD_REQUEST)
#
#         return Response({'Bad Request': 'Invalid post data, did not find a code key'}, status=status.HTTP_400_BAD_REQUEST)
#
#
# class CreateRoomView(APIView):
#     serializer_class = CreateRoomSerializer
#
#     def post(self, request, format=None):
#         if not self.request.session.exists(self.request.session.session_key):
#             self.request.session.create()
#
#         serializer = self.serializer_class(data=request.data)
#         if serializer.is_valid():
#             guest_can_pause = serializer.data.get('guest_can_pause')
#             votes_to_skip = serializer.data.get('votes_to_skip')
#             host = self.request.session.session_key
#             queryset = Room.objects.filter(host=host)
#             if queryset.exists():
#                 room = queryset[0]
#                 room.guest_can_pause = guest_can_pause
#                 room.votes_to_skip = votes_to_skip
#                 room.save(update_fields=['guest_can_pause', 'votes_to_skip'])
#                 self.request.session['room_code'] = room.code
#                 return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)
#             else:
#                 room = Room(host=host, guest_can_pause=guest_can_pause,
#                             votes_to_skip=votes_to_skip)
#                 room.save()
#                 self.request.session['room_code'] = room.code
#                 return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)
#
#         return Response({'Bad Request': 'Invalid data...'}, status=status.HTTP_400_BAD_REQUEST)
#
#
# class UserInRoom(APIView):
#     def get(self, request, format=None):
#         if not self.request.session.exists(self.request.session.session_key):
#             self.request.session.create()
#
#         data = {
#             'code': self.request.session.get('room_code')
#         }
#         return JsonResponse(data, status=status.HTTP_200_OK)
#
#
# class LeaveRoom(APIView):
#     def post(self, request, format=None):
#         if 'room_code' in self.request.session:
#             self.request.session.pop('room_code')
#             host_id = self.request.session.session_key
#             room_results = Room.objects.filter(host=host_id)
#             if len(room_results) > 0:
#                 room = room_results[0]
#                 room.delete()
#
#         return Response({'Message': 'Success'}, status=status.HTTP_200_OK)
#
#
# class UpdateRoom(APIView):
#     serializer_class = UpdateRoomSerializer
#
#     def patch(self, request, format=None):
#         if not self.request.session.exists(self.request.session.session_key):
#             self.request.session.create()
#
#         serializer = self.serializer_class(data=request.data)
#         if serializer.is_valid():
#             guest_can_pause = serializer.data.get('guest_can_pause')
#             votes_to_skip = serializer.data.get('votes_to_skip')
#             code = serializer.data.get('code')
#
#             queryset = Room.objects.filter(code=code)
#             if not queryset.exists():
#                 return Response({'msg': 'Room not found.'}, status=status.HTTP_404_NOT_FOUND)
#
#             room = queryset[0]
#             user_id = self.request.session.session_key
#             if room.host != user_id:
#                 return Response({'msg': 'You are not the host of this room.'}, status=status.HTTP_403_FORBIDDEN)
#
#             room.guest_can_pause = guest_can_pause
#             room.votes_to_skip = votes_to_skip
#             room.save(update_fields=['guest_can_pause', 'votes_to_skip'])
#             return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)
#
#         return Response({'Bad Request': "Invalid Data..."}, status=status.HTTP_400_BAD_REQUEST)
