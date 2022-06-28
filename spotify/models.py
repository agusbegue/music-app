from djongo import models
from django.contrib.auth.models import AbstractUser
from rest_framework.authtoken.models import Token


class Job(models.Model):
    user_id = models.CharField(max_length=50)
    active = models.BooleanField()
    start_date = models.DateField()


class JobRun(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=150)
    debug = models.BooleanField()


class User(AbstractUser):
    id = models.CharField(max_length=30, db_index=True, primary_key=True)
    username = None
    password = None
    first_name = None
    last_name = None
    email = None
    USERNAME_FIELD = 'id'
    REQUIRED_FIELDS = []

    @staticmethod
    def create_or_update_user(token_data, user_data):
        token_object = SpotifyToken.objects.filter(user__id=user_data['user_id']).select_related('user')
        if token_object.exists():
            token_object.update(**token_data)
            token_object = token_object[0]
            token_object.save()
            user = token_object.user
        else:
            user = User(id=user_data.pop('user_id'))
            user.save()
            SpotifyToken(user=user, **token_data).save()
            UserProfile(user=user, **user_data).save()

        api_token, _ = Token.objects.get_or_create(user=user)
        return user, api_token

    def logout(self):
        Token.objects.get(user=self).delete()


class SpotifyToken(models.Model):
    user = models.OneToOneField(User, db_index=True, on_delete=models.CASCADE)

    access_token = models.CharField(max_length=150)
    refresh_token = models.CharField(max_length=150)
    token_expiry = models.DateTimeField()
    token_type = models.CharField(max_length=50)


class UserProfile(models.Model):
    user = models.OneToOneField(User, db_index=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    email = models.EmailField('Email address', unique=True)
    country = models.CharField(max_length=3)

    created_at = models.DateTimeField(auto_now_add=True)
    admin = models.BooleanField(default=False)
    last_login = models.DateTimeField(auto_now=True)

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


