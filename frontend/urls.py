from django.urls import path
from .views import index
from django.views.generic.base import RedirectView

app_name = 'frontend'

urlpatterns = [
    path('', index, name=''),
    path('login', index),
    path('charts', index),
    path('playlists', index),
    path('historic', index),
    # path('time-series', index),
    # path('favicon.ico', RedirectView.as_view(url='/static/frontend/favicon.ico'))
]
