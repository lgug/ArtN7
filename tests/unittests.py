from django.test import TestCase

from catalog.models import Movie


# Create your tests here.
class MovieTestCase(TestCase):

    def setUp(self):
        Movie.objects.create(title_text="The Great Dictator",
                             original_title_text="The Great Dictator",
                             year_integer=1940,
                             )
