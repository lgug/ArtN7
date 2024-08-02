import base64
import json
import random
import os.path
import shutil

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.http import JsonResponse, FileResponse
from django.shortcuts import render

import catalog.catalog_managment
from catalog.models import Movie, Country, Genre, Saga, Director, Screenwriter, Actor, File
from catalog.project_utils import integrity_management, logmanager, filemanager
from catalog.project_utils.filemanager import build_movie_folder_name, chunk_sorter
from catalog.project_utils.integrity_management import MovieSynthesis

SEPARATOR = " · "


def index(request):
    logmanager.new_event(request, logmanager.LogLevel.INFO, logmanager.Function.INDEX, "Opened the index page")
    return render(request, 'catalog/index.html')


def movie_details(request, movie_id):
    logmanager.new_event(request, logmanager.LogLevel.INFO, logmanager.Function.DETAILS,
                         f"Open details for movie with id {movie_id}.")

    movie = Movie.objects.get(id=movie_id)
    countries = Country.objects.filter(movie=movie)
    countries_str = SEPARATOR.join([str(x) for x in list(countries)])

    genres = Genre.objects.filter(movie=movie)
    genres_str = SEPARATOR.join([str(x) for x in list(genres)])

    saga = Saga.objects.filter(movie=movie)
    saga_str = saga[0].name_text if len(saga) > 0 else ""

    directors = Director.objects.filter(movie=movie)
    directors_str = SEPARATOR.join([str(x) for x in list(directors)])

    screenwriters = Screenwriter.objects.filter(movie=movie)
    screenwriters_str = SEPARATOR.join([str(x) for x in list(screenwriters)])

    actors = Actor.objects.filter(movie=movie)
    actors_str = SEPARATOR.join([str(x) for x in list(actors)])

    context = {"movie": movie,
               "countries": countries_str,
               "genres": genres_str,
               "saga": saga_str,
               "directors": directors_str,
               "screenwriters": screenwriters_str,
               "actors": actors_str,
               "videos": get_all_videos(movie),
               "other_files": get_all_other_files(movie)}
    return render(request, "catalog/details.html", context)


def get_all_videos(movie):
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
    logmanager.new_event(request, logmanager.LogLevel.INFO, logmanager.Function.UPLOAD, "Open the Upload page")

    return render(request, "catalog/upload.html")


def upload_function(request):
    logmanager.new_event(request, logmanager.LogLevel.INFO, logmanager.Function.UPLOAD, "Start to save a new movie")

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
        logmanager.new_event(request, logmanager.LogLevel.ERROR, logmanager.Function.UPLOAD,
                             f"Error trying to save a new movie: {str(e)}")

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
    logmanager.new_event(request, logmanager.LogLevel.INFO, logmanager.Function.UPLOAD, str(movie.id))
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
    logmanager.new_event(request, logmanager.LogLevel.INFO, logmanager.Function.UPLOAD,
                         f"Uploading of new file with name {name} in the temp folder.")
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
    logmanager.new_event(request, logmanager.LogLevel.INFO, logmanager.Function.UPLOAD,
                         f"Removing temp file with name {name} from the temp folder.")
    if os.path.exists(f"temp/{name}"):
        os.remove(f"temp/{name}")
    return JsonResponse({'status': 'ok'})


def imdb_search(request, imdb_id):
    logmanager.new_event(request, logmanager.LogLevel.INFO, logmanager.Function.UPLOAD,
                         f"Searching information from IMDb for id {imdb_id}.")

    return JsonResponse(catalog.catalog_managment.retrieve_info_from_imdb(imdb_id))


def download_file(request, movie_id, name):
    logmanager.new_event(request, logmanager.LogLevel.INFO, logmanager.Function.DOWNLOAD,
                         f"Start downloading of file with name {name} (movie id: {movie_id}).")

    folder = [x for x in os.listdir('data') if x.startswith(str(movie_id))]
    if len(folder) > 0:
        return FileResponse(open(f"data/{folder[0]}/{name}", 'rb'), as_attachment=True)
    else:
        return None


@staff_member_required
def download_log_file(request):
    logmanager.new_event(request, logmanager.LogLevel.INFO, logmanager.Function.ADMIN,
                         "Request to download the log file.")

    if os.path.exists(f"{logmanager.LOG_FOLDER}/{logmanager.LOG_FILE}"):
        return FileResponse(open(f"{logmanager.LOG_FOLDER}/{logmanager.LOG_FILE}", 'rb'), as_attachment=True)
    else:
        return None


@staff_member_required
def download_catalog_report(request):
    report = {"movies": [], "info": []}

    movies = Movie.objects.all()
    for movie in movies:
        report["movies"].append({
            "id": movie.id,
            "title": movie.title_text,
            "original_title": movie.original_title_text,
            "year": movie.year_integer,
            "imdb_id": movie.imdb_id_text,
            "files": [{
                "file_name": x.file_name_text,
                "file_hash": x.hash_text
            } for x in File.objects.filter(movie_id__exact=movie.id)]
        })

    if not os.path.exists("temp"):
        os.makedirs("temp")
    with open("temp/report.json", 'w') as outfile:
        outfile.write(json.dumps(report))

    return FileResponse(open("temp/report.json", 'rb'), as_attachment=True)


def search(request):
    logmanager.new_event(request, logmanager.LogLevel.INFO, logmanager.Function.SEARCH,
                         "Open Search page.")

    return render(request, 'catalog/search.html', context={"results": {}})


def get_search_result(request):
    title = request.POST['formMovieTitle']
    year = request.POST['formMovieYear']
    saga = request.POST['formMovieSaga']
    director = request.POST['formMovieDirector']
    actor = request.POST['formMovieActor']

    logmanager.new_event(request, logmanager.LogLevel.INFO, logmanager.Function.SEARCH,
                         f"Start searching movies with title='{title}', year='{year}', saga='{saga}', director='{director}', actor='{actor}'")

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


def play_video(request, movie_id, name):  # TODO serve?
    folder = [x for x in os.listdir('data') if x.startswith(str(movie_id))]
    extension = name[name.rfind(".") + 1:]

    context = {
        'path': f"data/{folder[0]}/{name}",
        "type": f"video/{extension}"
    }
    return render(request, 'catalog/player.html', context)


def update_rating(request, movie_id):
    logmanager.new_event(request, logmanager.LogLevel.INFO, logmanager.Function.UPLOAD,
                         f"Update rating of movie with id {movie_id}.")

    new_rating = int(request.POST['rating'])
    movie = Movie.objects.get(pk=movie_id)
    movie.rating_integer = new_rating
    movie.save()

    return JsonResponse({'status': 'ok'})


def check_catalog_integrity(request):
    logmanager.new_event(request, logmanager.LogLevel.INFO, logmanager.Function.INTEGRITY_CHECK,
                         "Open catalog integrity check.")

    movies = integrity_management.get_all_movie_synthesis()
    context = {'movies': [m.to_json() for m in movies]}

    return render(request, 'catalog/integrity.html', context=context)


def check_movie_hash(request, movie_id):
    logmanager.new_event(request, logmanager.LogLevel.INFO, logmanager.Function.INTEGRITY_CHECK,
                         f"Started integrity check of movie with id {movie_id}")

    movie_s = MovieSynthesis.from_json(request.body.decode('utf-8'))
    response = integrity_management.check_movie(movie_s)

    return JsonResponse([x.to_dict() for x in response], safe=False)


def check_file_hash(request):
    file_info = json.loads(request.body.decode('utf-8'))
    logmanager.new_event(request, logmanager.LogLevel.INFO, logmanager.Function.INTEGRITY_CHECK,
                         f"Started integrity check of file with hash {file_info['hash']}")

    file = File.objects.filter(hash_text__iexact=file_info['hash'])[0]

    integrity_result = integrity_management.FileIntegrityCheckResult(file_info['movie_id'],
                                                                     file.file_name_text,
                                                                     file.hash_text)
    integrity_result.check_file()

    return JsonResponse(integrity_result.to_dict())


def suggested(request):
    logmanager.new_event(request, logmanager.LogLevel.INFO, logmanager.Function.SUGGESTED,
                         "Open Suggested movies page.")

    id_rating_list = list(Movie.objects.values_list('id', 'rating_integer'))
    ids = [i[0] for i in id_rating_list]

    selected_movies = []
    while len(selected_movies) < len(ids) and len(selected_movies) < 20:
        random_id = random.choices(ids, weights=[i[1] for i in id_rating_list], k=1)

        if len(random_id) > 0 and random_id[0] not in selected_movies:
            selected_movies.append(random_id[0])

    context = {'movies': list(Movie.objects.filter(id__in=selected_movies))}
    return render(request, 'catalog/suggested.html', context)


def download_all_movie_files(request, movie_id):
    logmanager.new_event(request, logmanager.LogLevel.INFO, logmanager.Function.DOWNLOAD,
                         f"Request downloading of all files for movie with id {movie_id}.")

    folder = filemanager.build_movie_folder_name(Movie.objects.get(pk=movie_id))
    shutil.make_archive("temp/archive", 'zip', folder)

    return FileResponse(open('temp/archive.zip', 'rb'), as_attachment=True)
