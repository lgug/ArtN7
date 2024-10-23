from django.test import TestCase

from catalog.models import Movie


# Create your tests here.
class MovieTestCase(TestCase):

    def setUp(self):
        Movie.objects.create(local_title="The Great Dictator",
                             original_title="The Great Dictator",
                             production_year=1940,
                             )
