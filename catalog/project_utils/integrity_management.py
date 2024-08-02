import json
from typing import List

from django.db import models
from django.db.models import Model

from catalog.catalog_managment import sha256sum
from catalog.models import Movie, File
from catalog.project_utils.filemanager import build_movie_folder_name


class FileSynthesis:
    def __init__(self, file_name, movie_id, file_hash):
        self.file_name = file_name
        self.movie_id = movie_id
        self.hash = file_hash

    def to_dict(self):
        return {
            'file_name': self.file_name,
            'file_hash': self.hash,
            'movie_id': self.movie_id
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            file_name=data['file_name'],
            movie_id=data['movie_id'],
            file_hash=data['file_hash']
        )

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_data):
        data = json.loads(json_data)
        return cls.from_dict(data)


class MovieSynthesis:

    def __init__(self, movie_id, title, original_title, year, files: List[FileSynthesis]):
        self.movie_id = movie_id
        self.title = title
        self.original_title = original_title
        self.year = year
        self.files = files

    def to_dict(self):
        return {
            'movie_id': self.movie_id,
            'title': self.title,
            'original_title': self.original_title,
            'year': self.year,
            'files': [f.to_dict() for f in self.files]
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            movie_id=data['movie_id'],
            title=data['title'],
            original_title=data['original_title'],
            year=data['year'],
            files=[FileSynthesis.from_dict(f) for f in data['files']]
        )

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_data):
        data = json.loads(json_data)
        return cls.from_dict(data)


class FileIntegrityCheckResult:

    def __init__(self, movie_id, file_name, expected_hash, actual_hash=None, whole=None):
        self.movie_id = movie_id
        self.file_name = file_name
        self.expected_hash = expected_hash
        self.actual_hash = actual_hash
        self.whole = whole

    def check_file(self):
        folder = build_movie_folder_name(Movie.objects.get(pk=self.movie_id), self.file_name)
        self.actual_hash = sha256sum(folder)
        self.whole = self.actual_hash.upper() == self.expected_hash.upper()

    def is_whole(self):
        return self.whole

    def to_dict(self):
        return {
            'movie_id': self.movie_id,
            'file_name': self.file_name,
            'expected_hash': self.expected_hash,
            'actual_hash': self.actual_hash,
            'whole': self.whole
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            movie_id=data['movie_id'],
            file_name=data['file_name'],
            expected_hash=data['expected_hash'],
            actual_hash=data['actual_hash'],
            whole=data['whole']
        )

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_data):
        data = json.loads(json_data)
        return cls.from_dict(data)


def check_movie(movie_synthesis: MovieSynthesis):
    result = []
    for file in movie_synthesis.files:
        res = FileIntegrityCheckResult(file.movie_id, file.file_name, file.hash)
        res.check_file()
        result.append(res)

    return result


def get_all_movie_synthesis():
    movies = Movie.objects.all()
    synthesis = [MovieSynthesis(movie.id,
                                movie.title_text,
                                movie.original_title_text,
                                movie.year_integer,
                                [FileSynthesis(f.file_name_text,
                                               movie.id,
                                               f.hash_text)
                                 for f in list(movie.file_set.all())])
                 for movie in movies]
    return synthesis
