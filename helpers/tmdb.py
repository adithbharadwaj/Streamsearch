from urllib.parse import urljoin, urlencode

import requests

TMDB_BASE_URL = 'https://api.themoviedb.org/'
TMDB_API_KEY = '00e967be34501054c5adb40c77221a4c'

def send_search_request(query):
    endpoint = '3/search/multi'
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'en-US',
        'query': query,
        'page': 1,
        'include_adult': 'false'
    }

    return requests.get(urljoin(TMDB_BASE_URL, endpoint), params=params).json()
