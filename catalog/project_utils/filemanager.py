import os
import shutil

DATA_ROOT = 'data'
TEMP_ROOT = 'temp'

MOVIE_FOLDER_DELIMITER = '__'


def chunk_sorter(e):
    return int(e)


def sanitize_filename(filename, tag, extra_char=" ()"):
    filename = (filename.replace('<', '')
                .replace('>', '')
                .replace(':', '')
                .replace('"', '')
                .replace('/', '')
                .replace('\\', '')
                .replace('|', '')
                .replace('?', '*'))
    tag = tag + extra_char

    if len(filename) == 0:
        filename = "Unencodable movie title"

    tag_len_in_bytes = len(tag.encode('utf-8'))
    filename_len_in_bytes = len(filename.encode('utf-8'))
    while filename_len_in_bytes + tag_len_in_bytes > 230:
        filename = filename[:-1]
        filename_len_in_bytes = len(filename.encode('utf-8'))

    return filename


def delete_all_movie_files(movie_path_folder):
    delete_single_file(movie_path_folder)


def delete_single_file(path):
    shutil.rmtree(path)


def build_movie_folder_name(movie_model, filename=''):
    movie_id = movie_model.id
    movie_name = sanitize_filename(movie_model.title_text, str(movie_id), extra_char=MOVIE_FOLDER_DELIMITER)

    return f'{DATA_ROOT}/{movie_id}{MOVIE_FOLDER_DELIMITER}{movie_name}/{filename}'


def check_temp_folder():
    if not os.path.exists(TEMP_ROOT):
        os.makedirs(TEMP_ROOT)


def clear_temp_folder():
    shutil.rmtree(TEMP_ROOT)
