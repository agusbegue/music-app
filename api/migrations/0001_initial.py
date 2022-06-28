# Generated by Django 3.1.12 on 2022-06-28 12:53

import api.models
from django.db import migrations, models
import djongo.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
                ('followers', models.BigIntegerField()),
                ('images', djongo.models.fields.JSONField()),
                ('genres', djongo.models.fields.JSONField()),
                ('created_at', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ArtistPopularity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('artist', djongo.models.fields.EmbeddedField(model_container=api.models.ArtistBasic)),
                ('popularity', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=30)),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Track',
            fields=[
                ('id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('artists', djongo.models.fields.ArrayField(model_container=api.models.ArtistBasic)),
                ('release_date', models.DateField()),
                ('forgotten', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='TrackRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('records', djongo.models.fields.ArrayField(model_container=api.models.Record)),
                ('track', djongo.models.fields.EmbeddedField(model_container=api.models.TrackBasic)),
            ],
        ),
    ]
