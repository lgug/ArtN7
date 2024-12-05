import ffmpeg
import csv
import json
import os.path
import random
import shutil
import magic

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.http import JsonResponse, FileResponse
from django.shortcuts import render

import catalog.catalog_managment
import catalog.project_utils.imdb_manager
from catalog.models import Movie, Country, Genre, Saga, Director, Screenwriter, Actor, File, FILE_TYPE_VIDEO_KEY
from catalog.project_utils import integrity_management, logmanager, filemanager, data_validation, imdb_manager
from catalog.project_utils.filemanager import TEMP_ROOT, \
    TEMP_META_FILE, DATA_ROOT, TEMP_ZIP_FILE, check_temp_folder, REPORT_FILE
from catalog.project_utils.http_manager import HEADER_CHUNK_NUMBER, HEADER_MOVIE_TYPE, \
    HEADER_MOVIE_TAG
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
    saga_str = saga[0].saga if len(saga) > 0 else ""

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
        files = File.objects.filter(movie=movie, type=File.TYPE_CHOICES[FILE_TYPE_VIDEO_KEY])
        for file in files:
            _map.append({"path": os.path.abspath(f"{file.folder}/{file.filename}"), "file": file})
        return _map
    except File.DoesNotExist:
        return []


def get_all_other_files(movie):
    _map = []

    try:
        not_videos = File.objects.exclude(type=File.TYPE_CHOICES[FILE_TYPE_VIDEO_KEY]).filter(movie=movie)
        for file in not_videos:
            _map.append({"path": os.path.abspath(f"{file.folder}/{file.filename}"), "file": file})
        return _map
    except File.DoesNotExist:
        return []


def movie_upload(request):
    logmanager.new_event(request, logmanager.LogLevel.INFO, logmanager.Function.UPLOAD, "Open the Upload page")

    return render(request, "catalog/upload.html")


def upload_function(request):
    logmanager.new_event(request, logmanager.LogLevel.INFO, logmanager.Function.UPLOAD, "Start to save a new movie")

    check, message = data_validation.validate_input_data(request.POST)
    if not check:
        logmanager.new_event(request, logmanager.LogLevel.ERROR, logmanager.Function.UPLOAD,
                             "Upload check has not passed")
        context = {"movie_id": None, "success": check, "message": message}
        return render(request, 'catalog/upload_result.html', context)

    local_title = request.POST["title"]
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

    movie = Movie(local_title=local_title,
                  original_title=original_title,
                  production_year=year,
                  user_rating=rating,
                  poster=poster,
                  imdb_id=imdb_id)
    movie.save()

    try:
        print("saving file...")
        catalog.catalog_managment.save_movie_files(movie)
    except Exception as e:
        logmanager.new_event(request, logmanager.LogLevel.ERROR, logmanager.Function.UPLOAD,
                             f"Error trying to save a new movie: {e}")

        movie.delete()
        context = {"movie_id": None, "success": False, "message": str(e)}
        return render(request, 'catalog/upload_result.html', context)

    for director in directors:
        d = Director(director_name=director, movie=movie)
        d.save()
    for actor in actors:
        a = Actor(actor_name=actor, movie=movie)
        a.save()
    for screenwriter in screenwriters:
        s = Screenwriter(screenwriter_name=screenwriter, movie=movie)
        s.save()

    for country in countries:
        c = Country(country_name=country, movie=movie)
        c.save()
    for genre in genres:
        g = Genre(genre=genre, movie=movie)
        g.save()

    if saga is not None:
        sg = Saga(saga=saga, movie=movie)
        sg.save()

    context = {"movie_id": movie.id, "success": True, "message": "OK"}
    logmanager.new_event(request, logmanager.LogLevel.INFO, logmanager.Function.UPLOAD, str(movie.id))
    return render(request, 'catalog/upload_result.html', context)


def upload_temp_file_chunk(request, name):
    # filemanager.check_temp_movie_folder(name)
    filemanager.check_temp_folder()

    chunk_number = request.headers[HEADER_CHUNK_NUMBER]
    print("Saving chunk n. " + str(chunk_number))
    content = request.body

    with open(f"{TEMP_ROOT}/{name}", "ab") as final_file:
        final_file.write(content)

    # with open(f'temp/D_{name}/{chunk_number}', 'wb') as destination:
    #     destination.write(content)

    return JsonResponse({'status': 'ok'})


def upload_temp_file(request, name):
    logmanager.new_event(request, logmanager.LogLevel.INFO, logmanager.Function.UPLOAD,
                         f"Uploading of new file with name {name} in the temp folder.")
    type_file = request.headers[HEADER_MOVIE_TYPE]
    tag = request.headers[HEADER_MOVIE_TAG]
    if tag == '':
        tag = 'Original'

    with open(f"{TEMP_ROOT}/{TEMP_META_FILE}", 'a') as meta:
        meta.write(f"{name};{type_file};{tag}\n")

    print("file saved successfully")
    return JsonResponse({'status': 'ok'})


def remove_temp_file(request, name):
    logmanager.new_event(request, logmanager.LogLevel.INFO, logmanager.Function.UPLOAD,
                         f"Removing temp file with name {name} from the temp folder.")
    if os.path.exists(f"{TEMP_ROOT}/{name}"):
        os.remove(f"{TEMP_ROOT}/{name}")

    meta_file = []
    with open(f"{TEMP_ROOT}/{TEMP_META_FILE}", newline='') as meta:
        meta_csv = csv.DictReader(meta, delimiter=';', fieldnames=['filename', 'type', 'tag'])
        for row in meta_csv:
            if row['filename'] != name:
                meta_file.append(row)

    with open(f"{TEMP_ROOT}/{TEMP_META_FILE}", "w", newline='') as meta:
        writer = csv.DictWriter(meta, delimiter=';', fieldnames=['filename', 'type', 'tag'])
        writer.writerows(meta_file)

    return JsonResponse({'status': 'ok'})


def imdb_search(request, imdb_id):
    logmanager.new_event(request, logmanager.LogLevel.INFO, logmanager.Function.UPLOAD,
                         f"Searching information from IMDb for id {imdb_id}.")

    return JsonResponse(imdb_manager.retrieve_info_from_imdb(imdb_id))


def download_file(request, movie_id, name):
    logmanager.new_event(request, logmanager.LogLevel.INFO, logmanager.Function.DOWNLOAD,
                         f"Start downloading of file with name {name} (movie id: {movie_id}).")

    folder = [x for x in os.listdir(DATA_ROOT) if x.startswith(str(movie_id))]
    if len(folder) > 0:
        return FileResponse(open(f"{DATA_ROOT}/{folder[0]}/{name}", 'rb'), as_attachment=True)
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
            "title": movie.local_title,
            "original_title": movie.original_title,
            "year": movie.production_year,
            "imdb_id": movie.imdb_id,
            "files": [{
                "file_name": x.filename,
                "file_hash": x.file_hash
            } for x in File.objects.filter(movie_id__exact=movie.id)]
        })

    check_temp_folder()
    with open(f"{TEMP_ROOT}/{REPORT_FILE}", 'w') as outfile:
        outfile.write(json.dumps(report))

    return FileResponse(open(f"{TEMP_ROOT}/{REPORT_FILE}", 'rb'), as_attachment=True)


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
        Q(local_title__icontains=title.lower()) |
        Q(original_title__icontains=title.lower())
    )
    if year != '' and int(year) > 0:
        result = result.filter(production_year__exact=int(year))
    if saga != '':
        result = result.filter(saga__saga__icontains=saga.lower())
    if director != '':
        result = result.filter(director__director_name__icontains=director.lower()).distinct()
    if actor != '':
        result = result.filter(actor__actor_name__icontains=actor.lower()).distinct()

    context = {'results': result}
    return render(request, 'catalog/search.html', context)


def update_rating(request, movie_id):
    logmanager.new_event(request, logmanager.LogLevel.INFO, logmanager.Function.UPLOAD,
                         f"Update rating of movie with id {movie_id}.")

    new_rating = int(request.POST['rating'])
    movie = Movie.objects.get(pk=movie_id)
    movie.user_rating = new_rating
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

    file = File.objects.filter(file_hash__iexact=file_info['hash'])[0]

    integrity_result = integrity_management.FileIntegrityCheckResult(file_info['movie_id'],
                                                                     file.filename,
                                                                     file.file_hash)
    integrity_result.check_file()

    return JsonResponse(integrity_result.to_dict())


def suggested(request):
    logmanager.new_event(request, logmanager.LogLevel.INFO, logmanager.Function.SUGGESTED,
                         "Open Suggested movies page.")

    id_rating_list = list(Movie.objects.values_list('id', 'user_rating'))
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
    shutil.make_archive(f"{TEMP_ROOT}/{TEMP_ZIP_FILE.split('.')[0]}",
                        f"{TEMP_ZIP_FILE.split('.')[1]}",
                        folder)

    return FileResponse(open(f'{TEMP_ROOT}/{TEMP_ZIP_FILE}', 'rb'), as_attachment=True)


def file_info(request, file_id):
    file = File.objects.get(pk=file_id)
    path = f"{file.folder}/{file.filename}"

    info = {
        "size": os.path.getsize(path),
        "last_modified": os.path.getmtime(path),
        "created": os.path.getctime(path),
        "type": magic.from_file(path, mime=True)
    }

    if file.type == File.TYPE_CHOICES[FILE_TYPE_VIDEO_KEY]:
        try:
            probe = ffmpeg.probe(path)
            video_info = [stream for stream in probe["streams"] if stream["codec_type"] == "video"]
            info['bitrate'] = probe['format']['bit_rate']
            info['duration'] = probe['format']['duration']
            if len(video_info) > 0:
                video_info = video_info[0]
                info['frame_rate'] = video_info['avg_frame_rate']
                info['codec'] = video_info['codec_long_name']
                info['aspect_ratio'] = video_info['display_aspect_ratio']
                info['width'] = video_info['width']
                info['height'] = video_info['height']
        except Exception as e:
            pass

    return JsonResponse(info)
