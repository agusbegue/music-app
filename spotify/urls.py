from django.urls import path
from .views import *

urlpatterns = [
    path('get-auth-url', AuthURL.as_view()),
    path('redirect', SpotifyCallback.as_view()),
    path('is-authenticated', IsAuthenticated.as_view()),
    path('logout', Logout.as_view()),
    path('get-data', GetData.as_view()),
    # path('current-song', CurrentSong.as_view()),
    # path('pause', PauseSong.as_view()),
    # path('play', PlaySong.as_view()),
    # path('skip', SkipSong.as_view())
]
