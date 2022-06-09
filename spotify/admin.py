from django.contrib import admin
from .models import User, UserProfile, SpotifyToken

admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(SpotifyToken)
