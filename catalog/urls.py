from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("movie/<int:movie_id>", views.movie_details, name="movie_detail"),
    path("new_movie", views.movie_upload, name="movie_upload"),
    path("upload_result", views.upload_function, name="upload_function"),
    path("imdb_search/<str:imdb_id>", views.imdb_search, name="imdb_search"),
    path("upload_temp_file/<str:name>", views.upload_temp_file, name="upload_temp_file"),
    path("remove_temp_file/<str:name>", views.remove_temp_file, name="remove_temp_file")
]