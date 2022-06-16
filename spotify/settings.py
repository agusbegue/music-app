
API_BASE_URL = "https://api.spotify.com/v1/"

REDIRECT_URI = "http://localhost:8000/spotify/redirect"

SCOPES = [
    # 'user-read-playback-state',
    # 'user-modify-playback-state',
    # 'user-read-currently-playing',
    'user-read-private',
    'user-read-email',
    'user-library-read',
    'playlist-read-private',
    'user-top-read'
]