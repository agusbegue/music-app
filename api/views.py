import numpy as np

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication

from spotify.auth import get_user_access_token
from spotify.interaction import (
    get_user_top_tracks, get_user_top_artists, get_user_playlists, get_playlists_data_v2, get_tracks_audio_features
)
from api.models import Track, Artist, ArtistPopularity


class GetTopTracksView(APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request, format=None):
        access_token = get_user_access_token(user_id=request.user.id)
        top_tracks = get_user_top_tracks(
            access_token,
            time_range=request.GET.get('time_range'),
            num_tracks=int(request.GET.get('amount'))
        )
        top_tracks_str = list(map(lambda f: f['name'] + ' - ' + ', '.join(f['artists']), top_tracks))
        return Response(top_tracks_str, status=status.HTTP_200_OK)


class GetTopArtistsView(APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request, format=None):
        access_token = get_user_access_token(user_id=request.user.id)
        top_artists = get_user_top_artists(
            access_token,
            time_range=request.GET.get('time_range'),
            num_artists=int(request.GET.get('amount')),
        )
        top_artists_str = list(map(lambda f: f['name'], top_artists))
        return Response(top_artists_str, status=status.HTTP_200_OK)


class GetUserPlaylists(APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request, format=None):
        access_token = get_user_access_token(user_id=request.user.id)
        playlists = get_user_playlists(access_token, owner_id=request.user.id)
        return Response(playlists, status=status.HTTP_200_OK)


class GetPlaylistAnalysisBoxplot(APIView):
    authentication_classes = [TokenAuthentication]
    features = [
        'danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness',
        'valence', 'tempo', 'popularity'
    ]

    def get(self, request, playlist_id):
        access_token = get_user_access_token(user_id=request.user.id)
        playlist_data = get_playlists_data_v2(access_token, [playlist_id], latest_n=30)[playlist_id]
        tracks_features = get_tracks_audio_features(
            access_token, list(map(lambda f: f['track_id'], playlist_data)),
            batch_size=30
        )  # {id: {tempo: ...
        popularities = {t['track_id']: t['popularity'] for t in playlist_data}
        tracks_features = {t_id: {**data, 'popularity': popularities[t_id]} for t_id, data in tracks_features.items()}
        boxplot_data = {'id': playlist_id, **self.get_boxplot_data(tracks_features)}
        return Response(boxplot_data, status=status.HTTP_200_OK)

    def get_boxplot_data(self, data):
        stats = {}
        for feature in self.features:
            array = np.array(list(map(lambda f: f[feature], data.values())))
            if feature == 'popularity':
                array = array[array != 0]
            quartile1 = np.percentile(array, 25)
            quartile3 = np.percentile(array, 75)
            iqr = quartile3 - quartile1
            bottom_mask = (array >= quartile1 - 1.5 * iqr)
            top_mask = (array <= quartile3 + 1.5 * iqr)
            stats[feature] = {
                'whiskerLow': array[bottom_mask].min() if bottom_mask.sum() != 0 else array[~bottom_mask].max(),
                'quartile1': quartile1,
                'quartile2': np.median(array),
                'quartile3': quartile3,
                'whiskerHigh': array[top_mask].max() if top_mask.sum() != 0 else array[~top_mask].min()
            }
        return stats


class GetAllArtists(APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        artists = Artist.objects.all().values('id', 'name')[:200]
        artists = list(map(lambda f: {'id': f.get('id'), 'name': f.get('name')}, artists))
        return Response(artists, status=status.HTTP_200_OK)


class GetArtistsHistoricData(APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request, artist_id):
        records = ArtistPopularity.objects.filter(artist={"artist_id": artist_id}).values('date', 'popularity')
        records = list(map(lambda f: {'date': f.get('date'), 'value': f.get('popularity')}, records))
        start_date = min(list(map(lambda f: f['date'], records)))
        tracks = Track.objects.filter(artists={"artist_id":artist_id},release_date__gte=start_date).values('name','release_date')
        tracks = list(map(lambda f: {'track': f.get('name'), 'date': f.get('release_date')}, tracks))
        tracks = self.match_popularity(tracks, records)

        data = {"id": artist_id, "popularity": records, "releases": tracks}
        return Response(data, status=status.HTTP_200_OK)

    def match_popularity(self, tracks, records):
        result = []
        is_sorted = False
        for track in tracks:
            match = next(filter(lambda pop: pop['date'] == track['date'], records), None)
            if match:
                result.append({**track, 'popularity': match['value']})
            else:
                if not is_sorted:
                    records = sorted(records, key=lambda f: f['date'])
                    is_sorted = True
                index = next([i for i, d in enumerate(records) if d > track['date']], None)
                if not index or index == 0: continue
                new = records[index]
                old = records[index-1]
                popularity = (
                    old['value'] * (new['date'] - track['date']).days +
                    new['value'] * (track['date'] - old['date']).days
                ) / (new['date'] - old['date']).days
                result.append({**track, 'popularity': popularity})
        return result



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
