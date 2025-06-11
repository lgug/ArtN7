import os
import shutil
from distutils.command.check import check

DATA_ROOT = 'data'
TEMP_ROOT = 'temp'
TEMP_META_FILE = 'meta.csv'
TEMP_ZIP_FILE = 'archive.zip'
REPORT_FILE = 'report.json'

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
                .replace('?', ''))
    tag = tag + extra_char

    # check if starts with points
    while len(filename) > 0 and filename[0] == '.':
        filename = filename[1:]

    # check if ends with points
    while len(filename) > 0 and filename[-1] == '.':
        filename = filename[:-1]

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
    movie_name = sanitize_filename(movie_model.local_title, str(movie_id), extra_char=MOVIE_FOLDER_DELIMITER)

    return f'{DATA_ROOT}/{movie_id}{MOVIE_FOLDER_DELIMITER}{movie_name}/{filename}'


def check_temp_folder():
    if not os.path.exists(TEMP_ROOT):
        os.makedirs(TEMP_ROOT)


def clear_temp_folder():
    shutil.rmtree(TEMP_ROOT)


def check_data_folder():
    if not os.path.exists(DATA_ROOT):
        os.makedirs(DATA_ROOT)


def check_temp_movie_folder(movie_name):
    check_temp_folder()
    path = f"{TEMP_ROOT}/D_{movie_name}"
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

    return path