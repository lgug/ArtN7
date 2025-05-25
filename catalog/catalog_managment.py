import hashlib
import os.path
import shutil

from catalog.models import File
from catalog.project_utils.filemanager import sanitize_filename, TEMP_ROOT, check_data_folder, DATA_ROOT, \
    clear_temp_folder, TEMP_META_FILE, check_temp_folder, MOVIE_FOLDER_DELIMITER


def save_movie_files(movie):
    metadata = get_meta_file()
    temp_files = os.listdir(TEMP_ROOT)

    check_data_folder()

    movie_folder = sanitize_filename(movie.local_title, str(movie.id), extra_char=f"{MOVIE_FOLDER_DELIMITER}")
    movie_root_path = f"{DATA_ROOT}/{movie.id}{MOVIE_FOLDER_DELIMITER}{movie_folder}"
    if not os.path.exists(movie_root_path):
        os.mkdir(movie_root_path)

    for temp_file in temp_files:
        if temp_file not in metadata.keys():
            continue

        extension = temp_file[temp_file.rfind("."):]
        print("Calculating hash...")
        sha256 = sha256sum(f"{TEMP_ROOT}/{temp_file}")
        print(f"Calculated hash: {sha256}")
        tag = metadata[temp_file][1]

        movie_title = sanitize_filename(movie.local_title, tag)
        movie_title_ext = f"{movie_title} ({tag}){extension}"
        shutil.move(f"{TEMP_ROOT}/{temp_file}", f"{movie_root_path}/{movie_title_ext}")

        file_entity = File(filename=movie_title_ext,
                           movie=movie,
                           folder=movie_root_path,
                           type=File.TYPE_CHOICES[metadata[temp_file][0]],
                           tag=tag,
                           file_hash=sha256)
        file_entity.save()

    clear_temp_folder()


def sha256sum(file_path):
    h = hashlib.sha256()

    with open(file_path, 'rb') as file:
        while True:
            chunk = file.read(h.block_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest().upper()


def get_meta_file():
    elements = {}
    if not os.path.exists(f"{TEMP_ROOT}/{TEMP_META_FILE}"):
        return elements

    with open(f"{TEMP_ROOT}/{TEMP_META_FILE}", 'r') as f:
        lines = f.readlines()
    for line in lines:
        split = line.split(";")
        if len(split) == 3:
            elements[split[0]] = [split[1], split[2].replace('\n', '')]

    return elements
