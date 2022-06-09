from djongo import models


class Artist(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=30)
    followers = models.BigIntegerField()
    images = models.JSONField()
    genres = models.JSONField()
    created_at = models.DateField(auto_now_add=True)

    def to_basic(self):
        return ArtistBasic.from_artist(self)

    def get(self, field):
        return getattr(self, field)

    @staticmethod
    def create_from_dict(**kwargs):
        return Artist(**{**{key: kwargs.get(key) for key in Artist.get_fields()},
                         **{'followers': kwargs.get('followers')['total']}})

    @staticmethod
    def get_fields():
        return ['id', 'name', 'followers', 'images', 'genres']


class ArtistBasic(models.Model):
    name = models.CharField(max_length=30)
    artist_id = models.CharField(max_length=50)

    class Meta:
        abstract = True

    @staticmethod
    def from_artist(artist):
        return {'name': artist.get('name'), 'artist_id': artist.get('id')}


class ArtistPopularity(models.Model):
    date = models.DateField(auto_now_add=True)
    artist = models.EmbeddedField(ArtistBasic)
    popularity = models.IntegerField()


class Track(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=50)
    artists = models.ArrayField(ArtistBasic)
    release_date = models.DateField()
    images = models.JSONField()
    audio_features = models.JSONField()
    forgotten = models.BooleanField(default=False)

    def to_basic(self):
        return TrackBasic.from_track(self)

    def get(self, field):
        return getattr(self, field)

    @staticmethod
    def create_from_dict(**kwargs):
        track_data = {field: kwargs.get(field) for field in list(set(Track.get_fields(False)) & set(kwargs.keys()))}
        track_data['artists'] = [ArtistBasic.from_artist(artist) for artist in kwargs.get('artists', [])]
        return Track(**track_data)

    @staticmethod
    def get_fields(basic=True):
        basic_fields = ['id', 'name', 'artists', 'images', 'release_date']
        return basic_fields if basic else basic_fields + ['audio_features', 'forgotten']


class TrackBasic(models.Model):
    name = models.CharField()
    artist_names = models.CharField()
    release_date = models.DateField()
    track_id = models.CharField(max_length=50)

    class Meta:
        abstract = True

    @staticmethod
    def from_track(track):
        return {'name': track.get('name'), 'release_date': track.get('release_date'), 'track_id': track.get('id'),
                'artist_names': ', '.join([artist['name'] for artist in track.get('artists')])}


class Playlist(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    code = models.CharField(max_length=30)
    name = models.CharField(max_length=30)


class Record(models.Model):
    details = models.JSONField()
    score = models.IntegerField()

    class Meta:
        abstract = True

    @staticmethod
    def from_playlist(playlist_code, rank):
        return {'details': {'type': 'playlist', 'code': playlist_code}, 'score': rank}

    @staticmethod
    def from_popularity(popularity):
        return {'details': {'type': 'popularity'}, 'score': popularity}


class TrackRecord(models.Model):
    date = models.DateField(auto_now_add=True)
    records = models.ArrayField(Record)
    track = models.EmbeddedField(TrackBasic)



# def generate_unique_code():
#     length = 6
#     while True:
#         code = ''.join(random.choices(string.ascii_uppercase, k=length))
#         if Room.objects.filter(code=code).count() == 0:
#             break
#     return code

# class Room(models.Model):
#     code = models.CharField(
#         max_length=8, default=generate_unique_code, unique=True)
#     host = models.CharField(max_length=50, unique=True)
#     guest_can_pause = models.BooleanField(null=False, default=False)
#     votes_to_skip = models.IntegerField(null=False, default=1)
#     created_at = models.DateTimeField(auto_now_add=True)
#     current_song = models.CharField(max_length=50, null=True)
