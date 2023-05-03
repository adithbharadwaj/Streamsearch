from urllib.parse import urljoin

import requests

from .model import Media, MediaType, MediaAccessMode, Provider

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

def fetch_search_results(query, locale):
    results = send_search_request(query, locale)['results']
    results = map(Media.from_json, results)
    results = filter(lambda media: media is not None, results)  # Removing non-media results.
    results = sorted(results, key=lambda media: -media.popularity)  # Sorting by decreasing popularity.
    return results

def send_media_request(media_id, media_type):
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'en-US'
    }

    if media_type == MediaType.MOVIE:
        endpoint = f'{TMDB_VERSION}/movie/{media_id}'
        return requests.get(urljoin(TMDB_BASE_URL, endpoint), params=params).json()
    elif media_type == MediaType.TV:
        endpoint = f'{TMDB_VERSION}/tv/{media_id}'
        return requests.get(urljoin(TMDB_BASE_URL, endpoint), params=params).json()
    else:
        raise ValueError(f'media_type must be one of {MediaType.values()}, found {media_type}.')

def fetch_media(media_id, media_type):
    result = send_media_request(media_id, media_type)
    print(type(result))
    print(result.keys())
    return Media.from_json(result, media_type=media_type)

def send_providers_request(media_id, media_type):
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

def fetch_providers(media_id, media_type, locale):
    results = send_providers_request(media_id, media_type)['results']
    country_code = locale
    if country_code in results:
        results = results[country_code]
    else:
        return None

    return {
        MediaAccessMode.SUBSCRIBE.value: map(Provider.from_json, results.get(MediaAccessMode.SUBSCRIBE.value, [])),
        MediaAccessMode.RENT.value: map(Provider.from_json, results.get(MediaAccessMode.RENT.value, [])),
        MediaAccessMode.BUY.value: map(Provider.from_json, results.get(MediaAccessMode.BUY.value, []))
    }

def to_image_path(filename, size):
    if filename is not None:
        return urljoin(f'{TMDB_IMG_BASE_URL}', f'{size}/{filename.lstrip("/")}')
    else:
        return None
