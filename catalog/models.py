from django.db import models

FILE_TYPE_VIDEO_KEY = 'VIDEO'
FILE_TYPE_AUDIO_KEY = 'AUDIO'
FILE_TYPE_SUBS_KEY = 'SUBS'
FILE_TYPE_OTHER_KEY = 'OTHER'


class Movie(models.Model):
    local_title = models.CharField(max_length=2048)
    original_title = models.CharField(max_length=2048, null=True)
    production_year = models.IntegerField()
    poster = models.TextField()
    imdb_id = models.CharField(max_length=64)
    user_rating = models.IntegerField()

    def __str__(self):
        return f"{self.local_title} ({str(self.production_year)})"


class Country(models.Model):
    country_name = models.CharField(max_length=2048)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    def __str__(self):
        return self.country_name


class Director(models.Model):
    director_name = models.CharField(max_length=2048)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    def __str__(self):
        return self.director_name


class Actor(models.Model):
    actor_name = models.CharField(max_length=2048)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    def __str__(self):
        return self.actor_name


class Screenwriter(models.Model):
    screenwriter_name = models.CharField(max_length=2048)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    def __str__(self):
        return self.screenwriter_name


class Genre(models.Model):
    genre = models.CharField(max_length=128)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    def __str__(self):
        return self.genre


class Saga(models.Model):
    saga = models.CharField(max_length=128)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    def __str__(self):
        return self.saga


class File(models.Model):
    TYPE_CHOICES = {FILE_TYPE_VIDEO_KEY: 'Video',
                    FILE_TYPE_AUDIO_KEY: 'Audio',
                    FILE_TYPE_SUBS_KEY: 'Subtitles',
                    FILE_TYPE_OTHER_KEY: 'Other'}
    filename = models.CharField(max_length=2048)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    folder = models.CharField(max_length=1024, default="data")
    type = models.CharField(max_length=1024, choices=TYPE_CHOICES)
    tag = models.CharField(max_length=1024)
    file_hash = models.CharField(max_length=512)

    def __str__(self):
        return f"{self.filename} ({self.movie.local_title})"
