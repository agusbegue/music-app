from django.urls import path
from .views import index
from django.views.generic.base import RedirectView

app_name = 'frontend'

urlpatterns = [
    path('', index, name=''),
    path('playlists', index),
    path('info', index),
    path('join', index),
    path('create', index),
    path('room/<str:roomCode>', index),
    path('my-music', index),
    # path('favicon.ico', RedirectView.as_view(url='/static/frontend/favicon.ico'))
]
