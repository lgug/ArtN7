import base64
import os.path

from django.http import JsonResponse
from django.shortcuts import render

import catalog.catalog_managment
from catalog.models import *


def index(request):
    return render(request, 'catalog/index.html')


def movie_details(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    countries = Country.objects.filter(movie=movie)
    countries_str = " · ".join([str(x) for x in list(countries)])

    genres = Genre.objects.filter(movie=movie)
    genres_str = " · ".join([str(x) for x in list(genres)])

    directors = Director.objects.filter(movie=movie)
    directors_str = " · ".join([str(x) for x in list(directors)])

    screenwriters = Screenwriter.objects.filter(movie=movie)
    screenwriters_str = " · ".join([str(x) for x in list(screenwriters)])

    actors = Actor.objects.filter(movie=movie)
    actors_str = " · ".join([str(x) for x in list(actors)])

    context = {"movie": movie,
               "countries": countries_str,
               "genres": genres_str,
               "directors": directors_str,
               "screenwriters": screenwriters_str,
               "actors": actors_str}
    return render(request, "catalog/details.html", context)


def movie_upload(request):
    return render(request, "catalog/upload.html")


def upload_function(request):
    title = request.POST["title"]
    original_title = request.POST["original_title"] if request.POST["original_title"] != '' else None
    year = int(request.POST["year"])
    saga = request.POST["saga"] if request.POST["saga"] != '' else None
    directors = request.POST.getlist("directors")
    actors = request.POST.getlist("actors")
    screenwriters = request.POST.getlist("screenwriters")
    countries = request.POST.getlist("countries")
    genres = request.POST.getlist("genres")
    imdb_id = request.POST["imdb_id"]
    rating = int(request.POST["rating"])
    poster = request.POST["poster"]

    movie = Movie(title_text=title,
                  original_title_text=original_title,
                  year_integer=year,
                  rating_integer=rating,
                  poster_text=poster,
                  imdb_id_text=imdb_id)
    movie.save()

    try:
        catalog.catalog_managment.save_movie_files(movie)
    except Exception:
        movie.delete()
        return render(request, 'catalog/upload_result.html')

    for director in directors:
        d = Director(name_text=director, movie=movie)
        d.save()
    for actor in actors:
        a = Actor(name_text=actor, movie=movie)
        a.save()
    for screenwriter in screenwriters:
        s = Screenwriter(name_text=screenwriter, movie=movie)
        s.save()

    for country in countries:
        c = Country(country_text=country, movie=movie)
        c.save()
    for genre in genres:
        g = Genre(genre_text=genre, movie=movie)
        g.save()

    if saga is not None:
        sg = Saga(name_text=saga, movie=movie)
        sg.save()

    return render(request, 'catalog/upload_result.html')


def upload_temp_file(request, name):
    if not os.path.exists("temp"):
        os.mkdir("temp")

    type_file = request.headers['Movie-Type']
    tag = request.headers['Movie-Tag']
    content = request.body

    with open('temp/' + name, 'wb') as destination:
        destination.write(content)
    with open('temp/meta.csv', 'a') as meta:
        meta.write(f"{name};{type_file};{tag}\n")

    return JsonResponse({'status': 'ok'})


def remove_temp_file(request, name):
    if os.path.exists(f"temp/{name}"):
        os.remove(f"temp/{name}")
    return JsonResponse({'status': 'ok'})


def imdb_search(request, imdb_id):
    return JsonResponse(catalog.catalog_managment.retrieve_info_from_imdb(imdb_id))
