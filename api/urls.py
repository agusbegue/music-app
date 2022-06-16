from django.urls import path

from . import views

urlpatterns = [
    path('user-top-tracks', views.GetTopTracksView.as_view()),
    path('user-top-artists', views.GetTopArtistsView.as_view()),
    path('user-playlists', views.GetUserPlaylists.as_view()),
    path('playlist-boxplot/<str:playlist_id>', views.GetPlaylistAnalysisBoxplot.as_view()),
    # path('room', RoomView.as_view()),
    # path('create-room', CreateRoomView.as_view()),
    # path('get-room', GetRoom.as_view()),
    # path('join-room', JoinRoom.as_view()),
    # path('user-in-room', UserInRoom.as_view()),
    # path('leave-room', LeaveRoom.as_view()),
    # path('update-room', UpdateRoom.as_view())
]
