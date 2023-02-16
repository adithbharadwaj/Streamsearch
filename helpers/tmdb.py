from urllib.parse import urljoin

from helpers.parse import MediaType

import requests

TMDB_BASE_URL = 'https://api.themoviedb.org/'
TMDB_IMG_BASE_URL = 'https://image.tmdb.org/t/p/'
TMDB_API_KEY = '00e967be34501054c5adb40c77221a4c'
TMDB_VERSION = 3

def send_search_request(query, locale):
    endpoint = f'{TMDB_VERSION}/search/multi'
    params = {
        'api_key': TMDB_API_KEY,
        'query': query,
        'region': locale,
        'language': 'en-US',
        'page': 1,
        'include_adult': 'false'
    }

    return requests.get(urljoin(TMDB_BASE_URL, endpoint), params=params).json()


def send_metadata_request(media_id, media_type):
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'en-US'
    }

    if media_type == MediaType.MOVIE:
        endpoint = f'{TMDB_VERSION}/movie/{media_id}/watch/providers'
        return requests.get(urljoin(TMDB_BASE_URL, endpoint), params=params).json()
    elif media_type == MediaType.TV:
        endpoint = f'{TMDB_VERSION}/tv/{media_id}/watch/providers'
        return requests.get(urljoin(TMDB_BASE_URL, endpoint), params=params).json()
    else:
        raise ValueError(f'media_type must be one of {MediaType.values()}, found {media_type}.')

def to_image_path(filename, size):
    return urljoin(f'{TMDB_IMG_BASE_URL}', f'{size}/{filename.lstrip("/")}')
