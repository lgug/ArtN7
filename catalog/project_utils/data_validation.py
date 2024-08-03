from datetime import datetime


def validate_input_data(input_data):
    title = input_data['title']
    if title is None or title.strip() == '':
        return False, "A title must be provided"

    year = input_data['year']
    try:
        year = int(year)
        if year < 1850 or year > datetime.now().year:
            return False, "The year of production must be between 1850 and the current year"
    except ValueError:
        return False, "The year of production must be an integer"

    directors = input_data.getlist("directors")
    if directors is None or len(directors) == 0:
        return False, "At least one director is required"
    for director in directors:
        if director.strip() == '':
            return False, "Invalid director name inserted"

    genres = input_data.getlist("genres")
    if genres is None or len(genres) == 0:
        return False, "At least one genre is required"
    for genre in genres:
        if genre.strip() == '':
            return False, "Invalid genre inserted"

    countries = input_data.getlist("countries")
    if countries is None or len(countries) == 0:
        return False, "At least one country is required"
    for country in countries:
        if country.strip() == '':
            return False, "Invalid country inserted"

    rating = input_data['rating']
    try:
        rating = int(rating)
        if rating < 1 or rating > 10:
            return False, "Rating must be provided and must be between 1 and 10"
    except ValueError:
        return False, "Rating must be an integer"

    poster = input_data['poster']
    if poster is None or poster == '':
        return False, "A poster of the movie must be provided"

    return True, "OK"
