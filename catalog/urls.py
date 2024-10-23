from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("movie/<int:movie_id>", views.movie_details, name="movie_detail"),
    path("new_movie", views.movie_upload, name="movie_upload"),
    path("upload_result", views.upload_function, name="upload_function"),
    path("imdb_search/<str:imdb_id>", views.imdb_search, name="imdb_search"),
    path("upload_temp_file_chunk/<str:name>", views.upload_temp_file_chunk, name="upload_temp_file_chunk"),
    path("upload_temp_file/<str:name>", views.upload_temp_file, name="upload_temp_file"),
    path("remove_temp_file/<str:name>", views.remove_temp_file, name="remove_temp_file"),
    path("download_file/<int:movie_id>/<str:name>", views.download_file, name="download_file"),
    path("search", views.search, name="search"),
    path("search_result", views.get_search_result, name="get_search_result"),
    path("update_rating/<int:movie_id>", views.update_rating, name="update_rating"),
    path("check_catalog_integrity", views.check_catalog_integrity, name="check_catalog_integrity"),
    path("check_movie_hash/<int:movie_id>", views.check_movie_hash, name="check_movie_hash"),
    path("check_file_hash", views.check_file_hash, name="check_file_hash"),
    path("suggested_movies", views.suggested, name="suggested"),
    path("download_log_file", views.download_log_file, name="download_log_file"),
    path("download_catalog_report", views.download_catalog_report, name="download_catalog_report"),
    path("downloal_all_movie_files/<int:movie_id>", views.download_all_movie_files, name="download_all_movie_files"),
    path("file_info/<int:file_id>", views.file_info, name="file_info"),
]
