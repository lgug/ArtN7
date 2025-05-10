import pycountry
from pycountry import historic_countries
from difflib import SequenceMatcher

def get_current_countries():
    return list(pycountry.countries)

def get_historic_countries():
    historic = list(historic_countries)

    # workaround for West Germany code
    historic.append(pycountry.db.Country(alpha_2='XWG', alpha_3='XWG', alpha_4='XWG', name='West Germany'))

    return historic

def get_country_name(code, known_name=None):
    name = None
    countries = pycountry.countries
    historic = pycountry.historic_countries

    # workaround for West Germany code
    if code == 'XWG':
        return "West Germany"

    if len(code) == 2:
        result = countries.get(alpha_2=code)
        if result is None or (known_name is not None and SequenceMatcher(None, result, known_name).ratio() < 0.5):
            name = historic.get(alpha_2=code)
        else:
            name = result
    elif len(code) == 3:
        result = countries.get(alpha_3=code)
        if result is None or (known_name is not None and SequenceMatcher(None, result, known_name).ratio() < 0.5):
            name = historic.get(alpha_2=code)
        else:
            name = result
    elif len(code) == 4:
        name = historic.get(alpha_4=code)

    return None if name is None else name.name


if __name__ == '__main__':
    get_historic_countries()
    country = get_country_name('su', 'USSR')
    print(country)