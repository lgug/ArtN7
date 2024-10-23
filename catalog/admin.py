from django.contrib import admin
from django.utils.html import format_html

from .models import Movie, Genre, Actor, Director, Screenwriter, Saga, File
from .project_utils import logmanager
from .project_utils.filemanager import delete_all_movie_files, delete_single_file, build_movie_folder_name


@admin.action(description="Delete movie and all its files")
def delete_movie_and_files(modeladmin, request, queryset):
    logmanager.new_event(request, logmanager.LogLevel.INFO, logmanager.Function.ADMIN,
                         "Request to delete titles from the catalog.")

    for movie in queryset:
        path = build_movie_folder_name(movie)
        delete_all_movie_files(path)
        movie.delete()

        logmanager.new_event(request, logmanager.LogLevel.INFO, logmanager.Function.ADMIN,
                             f"The movie with id {movie.id} and title '{movie.local_title}' has been deleted.")


@admin.action(description="Delete this file from the catalog")
def delete_movie_file(modeladmin, request, queryset):
    logmanager.new_event(request, logmanager.LogLevel.INFO, logmanager.Function.ADMIN,
                         "Request to delete files from the catalog.")

    for file in queryset:
        path = build_movie_folder_name(file.movie, file.filename)
        delete_single_file(path)
        file.delete()

        logmanager.new_event(request, logmanager.LogLevel.INFO, logmanager.Function.ADMIN,
                             f"The file with name '{file.filename}' for movie with id {file.movie.id} has been deleted.")


class MovieAdmin(admin.ModelAdmin):
    actions = [delete_movie_and_files]
    list_display = ("__str__", "view_actors_list", "view_directors_list", "view_screenwriters_list", "view_files_list")

    def view_actors_list(self, obj):  # TODO implementare il link agli attori
        count = obj.actor_set.count()
        # url = reverse("admin:catalogs_movies_changelist" +
        #               "?" +
        #               urlencode({"movie__id": f"{obj.id}"})
        #               )
        return format_html('<a href="{}">{} Actors</a>', "", count)

    def view_directors_list(self, obj):  # TODO implementare il link ai registi
        count = obj.director_set.count()
        return format_html('<a href="{}">{} Directors</a>', "", count)

    def view_screenwriters_list(self, obj):  # TODO implementare il link agli sceneggiatori
        count = obj.screenwriter_set.count()
        return format_html('<a href="{}">{} Screenwriters</a>', "", count)

    def view_files_list(self, obj):  # TODO implementare il link ai file
        count = obj.file_set.count()
        return format_html('<a href="{}">{} Files</a>', "", count)

    view_actors_list.short_description = "Actors"
    view_directors_list.short_description = "Directors"
    view_screenwriters_list.short_description = "Screenwriters"
    view_files_list.short_description = "Files"


class FileAdmin(admin.ModelAdmin):
    actions = [delete_movie_file]


class ActorAdmin(admin.ModelAdmin):
    list_display = ("__str__", "movie")


class DirectorAdmin(admin.ModelAdmin):
    list_display = ("__str__", "movie")


admin.site.register(File, FileAdmin)
admin.site.register(Movie, MovieAdmin)
admin.site.register(Genre)
admin.site.register(Actor, ActorAdmin)
admin.site.register(Director, DirectorAdmin)
admin.site.register(Screenwriter)
admin.site.register(Saga)
