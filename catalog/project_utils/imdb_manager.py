import base64
import json

import requests
from bs4 import BeautifulSoup


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
            for c in json_data['mainColumnData']['countriesDetails']['countries']:
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