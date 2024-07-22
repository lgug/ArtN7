import base64
import random
import os.path
import shutil

from django.db.models import Q
from django.http import JsonResponse, FileResponse
from django.shortcuts import render

import catalog.catalog_managment
from catalog.models import *
from catalog.project_utils.filemanager import build_movie_folder_name, chunk_sorter


SEPARATOR = " · "


def index(request):
    return render(request, 'catalog/index.html')


def movie_details(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    countries = Country.objects.filter(movie=movie)
    countries_str = SEPARATOR.join([str(x) for x in list(countries)])

    genres = Genre.objects.filter(movie=movie)
    genres_str = SEPARATOR.join([str(x) for x in list(genres)])

    directors = Director.objects.filter(movie=movie)
    directors_str = SEPARATOR.join([str(x) for x in list(directors)])

    screenwriters = Screenwriter.objects.filter(movie=movie)
    screenwriters_str = SEPARATOR.join([str(x) for x in list(screenwriters)])

    actors = Actor.objects.filter(movie=movie)
    actors_str = SEPARATOR.join([str(x) for x in list(actors)])

    context = {"movie": movie,
               "countries": countries_str,
               "genres": genres_str,
               "directors": directors_str,
               "screenwriters": screenwriters_str,
               "actors": actors_str,
               "videos": get_all_movies(movie),
               "other_files": get_all_other_files(movie)}
    return render(request, "catalog/details.html", context)


def get_all_movies(movie):
    _map = []

    try:
        files = File.objects.filter(movie=movie, type_text='Video')
        for file in files:
            folder = [x for x in os.listdir('data') if x.startswith(str(file.movie.id))]
            _map.append({"path": os.path.abspath(f"data/{folder[0]}/{file.file_name_text}"), "file": file})
        return _map
    except File.DoesNotExist:
        return []


def get_all_other_files(movie):
    _map = []

    try:
        not_videos = File.objects.exclude(type_text="Video").filter(movie=movie)
        for file in not_videos:
            folder = [x for x in os.listdir('data') if x.startswith(str(file.movie.id))]
            _map.append({"path": os.path.abspath(f"data/{folder[0]}/{file.file_name_text}"), "file": file})
        return _map
    except File.DoesNotExist:
        return []


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
    except Exception as e:
        movie.delete()
        context = {"movie_id": None, "success": False, "message": str(e)}
        return render(request, 'catalog/upload_result.html', context)

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

    context = {"movie_id": movie.id, "success": True, "message": "OK"}
    return render(request, 'catalog/upload_result.html', context)


def upload_temp_file_chunk(request, name):
    if not os.path.exists(f"temp/D_{name}"):
        os.makedirs(f"temp/D_{name}", exist_ok=True)

    chunk_number = request.headers['Num-Chunk']
    content = request.body

    with open(f'temp/D_{name}/{chunk_number}', 'wb') as destination:
        destination.write(content)

    return JsonResponse({'status': 'ok'})


def upload_temp_file(request, name):
    type_file = request.headers['Movie-Type']
    tag = request.headers['Movie-Tag']

    chunk_files = os.listdir(f"temp/D_{name}")
    chunk_files.sort(key=chunk_sorter)
    for chunk in chunk_files:
        with open(f"temp/D_{name}/{chunk}", 'rb') as source:
            content = source.read()
        os.remove(f"temp/D_{name}/{chunk}")
        with open(f"temp/{name}", 'ab') as file:
            file.write(content)

    shutil.rmtree(f"temp/D_{name}")

    with open('temp/meta.csv', 'a') as meta:
        meta.write(f"{name};{type_file};{tag}\n")

    return JsonResponse({'status': 'ok'})


def remove_temp_file(request, name):
    if os.path.exists(f"temp/{name}"):
        os.remove(f"temp/{name}")
    return JsonResponse({'status': 'ok'})


def imdb_search(request, imdb_id):
    return JsonResponse(catalog.catalog_managment.retrieve_info_from_imdb(imdb_id))


def download_file(request, movie_id, name):
    folder = [x for x in os.listdir('data') if x.startswith(str(movie_id))]
    if len(folder) > 0:
        return FileResponse(open(f"data/{folder[0]}/{name}", 'rb'), as_attachment=True)
    else:
        return None


def search(request):
    return render(request, 'catalog/search.html', context={"results": {}})


def get_search_result(request):
    title = request.POST['formMovieTitle']
    year = request.POST['formMovieYear']
    saga = request.POST['formMovieSaga']
    director = request.POST['formMovieDirector']
    actor = request.POST['formMovieActor']

    result = Movie.objects.filter(
        Q(title_text__icontains=title.lower()) |
        Q(original_title_text__icontains=title.lower())
    )
    if year != '' and int(year) > 0:
        result = result.filter(year_integer__exact=int(year))
    if saga != '':
        result = result.filter(saga__name_text__icontains=saga.lower())
    if director != '':
        result = result.filter(director__name_text__icontains=director.lower()).distinct()
    if actor != '':
        result = result.filter(actor__name_text__icontains=actor.lower()).distinct()

    context = {'results': result}
    return render(request, 'catalog/search.html', context)


def play_video(request, movie_id, name):
    folder = [x for x in os.listdir('data') if x.startswith(str(movie_id))]
    extension = name[name.rfind(".") + 1:]

    context = {
        'path': f"data/{folder[0]}/{name}",
        "type": f"video/{extension}"
    }
    return render(request, 'catalog/player.html', context)


def update_rating(request, movie_id):
    new_rating = int(request.POST['rating'])
    movie = Movie.objects.get(pk=movie_id)
    movie.rating_integer = new_rating
    movie.save()

    return JsonResponse({'status': 'ok'})


def check_catalog_integrity(request):
    movies = Movie.objects.all()
    context = {'movies': [m.id for m in movies]}

    return render(request, 'catalog/integrity.html', context=context)


def check_movie_hash(request, movie_id):
    movie = Movie.objects.get(pk=movie_id)
    files = movie.file_set().all()
    response = {'files': []}

    for file in files:
        original_hash = file.hash_text

        file_path = build_movie_folder_name(movie, file.file_name_text)
        actual_hash = catalog.catalog_managment.sha256sum(file_path)

        response['files'].append(
            {'filename': file.file_name_text,
             'original_hash': original_hash,
             'actual_hash': actual_hash}
        )

    response['status'] = 'OK'
    return JsonResponse(response)


def suggested(request):
    id_rating_list = list(Movie.objects.values_list('id', 'rating_integer'))
    ids = [i[0] for i in id_rating_list]

    selected_movies = []
    while len(selected_movies) < len(ids) and len(selected_movies) < 20:
        random_id = random.choices(ids, weights=[i[1] for i in id_rating_list], k=1)

        if len(random_id) > 0 and random_id[0] not in selected_movies:
            selected_movies.append(random_id[0])

    context = {'movies': list(Movie.objects.filter(id__in=selected_movies))}
    return render(request, 'catalog/suggested.html', context)
