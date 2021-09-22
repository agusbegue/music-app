from django.db import models

NO_SESSION = ''


class SpotifyUser(models.Model):
    user_id = models.IntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=50)
    email = models.EmailField()

    created_at = models.DateTimeField(auto_now_add=True)
    admin = models.BooleanField(default=False)
    last_login = models.DateTimeField(auto_now_add=True)

    session_id = models.CharField(max_length=150)
    access_token = models.CharField(max_length=150)
    refresh_token = models.CharField(max_length=150)
    token_expiry = models.DateTimeField()
    token_type = models.CharField(max_length=50)

    def logout(self):
        self.session_id = NO_SESSION
        self.save()

    # @staticmethod
    # def create_or_update_user(token_data):
    #     # Only gets called after SpotifyCallback so access token is always valid
    #     user_data = get_spotify_user_data(access_token=token_data.get('access_token'))
    #     user = SpotifyUser.objects.filter(user_id=user_data.get('user_id'))
    #     if user.exists():
    #         user.update(**token_data)
    #     else:
    #         user = SpotifyUser(**user_data, **token_data)
    #         user.save()


