from django.db import models


class Movie(models.Model):
    title_text = models.CharField(max_length=1024)
    original_title_text = models.CharField(max_length=1024, null=True)
    year_integer = models.IntegerField()
    poster_text = models.TextField()
    imdb_id_text = models.CharField(max_length=64)
    rating_integer = models.IntegerField()

    def __str__(self):
        return self.title_text + " (" + str(self.year_integer) + ")"


class Country(models.Model):
    country_text = models.CharField(max_length=1024)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    def __str__(self):
        return self.country_text


class Director(models.Model):
    name_text = models.CharField(max_length=1024)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    def __str__(self):
        return self.name_text


class Actor(models.Model):
    name_text = models.CharField(max_length=1024)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    def __str__(self):
        return self.name_text


class Screenwriter(models.Model):
    name_text = models.CharField(max_length=1024)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    def __str__(self):
        return self.name_text


class Genre(models.Model):
    genre_text = models.CharField(max_length=1024)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    def __str__(self):
        return self.genre_text


class Saga(models.Model):
    name_text = models.CharField(max_length=1024)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    def __str__(self):
        return self.name_text


class File(models.Model):
    file_name_text = models.CharField(max_length=2048)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    type_text = models.CharField(max_length=1024)
    tag_text = models.CharField(max_length=1024)
    hash_text = models.CharField(max_length=512)

    def __str__(self):
        return self.file_name_text
