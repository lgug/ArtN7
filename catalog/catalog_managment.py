import base64
import hashlib
import json
import os.path
import shutil

from bs4 import BeautifulSoup
import requests

from catalog.models import File
from catalog.project_utils.filemanager import sanitize_filename


def retrieve_info_from_imdb(imdb_id):
    movie_info = {}

    url = f'https://www.imdb.com/title/{imdb_id}/'
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows)'})
    soup = BeautifulSoup(response.text, "html.parser")
    script_tags = soup.select('script')
    for st in script_tags:
        if 'type' in st.attrs and st.get('type') == 'application/ld+json':
            json_data = json.loads(st.text)
            image = requests.get(json_data['image']).content
            movie_info['poster'] = base64.b64encode(image).decode()
        elif 'id' in st.attrs and st.get('id') == '__NEXT_DATA__':
            json_data = json.loads(st.text)['props']['pageProps']
            movie_info['title'] = json_data['aboveTheFoldData']['titleText']['text']
            movie_info['original_title'] = json_data['aboveTheFoldData']['originalTitleText']['text']
            movie_info['year'] = json_data['aboveTheFoldData']['releaseYear']['year']

            countries = []
            for c in json_data['mainColumnData']['countriesOfOrigin']['countries']:
                countries.append(c['id'])
            movie_info['countries'] = countries

            genres = []
            for g in json_data['aboveTheFoldData']['genres']['genres']:
                genres.append(g['text'])
            movie_info['genres'] = genres

            directors = []
            for d in json_data['mainColumnData']['directors']:
                for d1 in d['credits']:
                    directors.append(d1['name']['nameText']['text'])
            movie_info['directors'] = directors

            screenwriters = []
            for s in json_data['mainColumnData']['writers']:
                for s1 in s['credits']:
                    screenwriters.append(s1['name']['nameText']['text'])
            movie_info['screenwriters'] = screenwriters

            actors = []
            for a in json_data['mainColumnData']['cast']['edges']:
                actors.append(a['node']['name']['nameText']['text'])
            movie_info['actors'] = actors

    return movie_info


def save_movie_files(movie):
    metadata = get_meta_file()
    temp_files = os.listdir("temp")

    if not os.path.exists("data"):
        os.mkdir("data")

    movie_folder = sanitize_filename(movie.title_text, str(movie.id), extra_char="__")
    movie_root_path = f"data/{movie.id}__{movie_folder}"
    if not os.path.exists(movie_root_path):
        os.mkdir(movie_root_path)

    for temp_file in temp_files:
        if temp_file not in metadata.keys():
            continue

        extension = temp_file[temp_file.rfind("."):]
        sha256 = sha256sum(f"temp/{temp_file}")
        tag = metadata[temp_file][1]

        movie_title = sanitize_filename(movie.title_text, tag)
        movie_title_ext = f"{movie_title} ({tag}){extension}"
        shutil.move(f"temp/{temp_file}", f"{movie_root_path}/{movie_title_ext}")

        file_entity = File(file_name_text=movie_title_ext,
                           movie=movie,
                           type_text=File.TYPE_CHOICES[metadata[temp_file][0]],
                           tag_text=tag,
                           hash_text=sha256)
        file_entity.save()

    shutil.rmtree("temp")


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
    with open('temp/meta.csv', 'r') as f:
        lines = f.readlines()

    for line in lines:
        split = line.split(";")
        if len(split) == 3:
            elements[split[0]] = [split[1], split[2].replace('\n', '')]

    return elements
