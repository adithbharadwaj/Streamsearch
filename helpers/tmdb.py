from functools import reduce
from urllib.parse import urljoin

import requests

from .model import Media, MediaAccessMode, MediaType, Provider

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

def send_movie_genre_mapping_request():
    endpoint = f'{TMDB_VERSION}/genre/movie/list'
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'en-US'
    }

    return requests.get(urljoin(TMDB_BASE_URL, endpoint), params=params).json()

def send_tv_genre_mapping_request():
    endpoint = f'{TMDB_VERSION}/genre/tv/list'
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'en-US'
    }

    return requests.get(urljoin(TMDB_BASE_URL, endpoint), params=params).json()

def generate_genre_map():
    genre_map = {}

    movie_genres = send_movie_genre_mapping_request()['genres']
    tv_genres = send_tv_genre_mapping_request()['genres']

    for genre in movie_genres:
        genre_map[genre['name']] = genre['id']

    for genre in tv_genres:
        genre_map[genre['name']] = genre['id']

    return genre_map

def generate_genre_list():
    genre_list = ["All Genres"]

    movie_genres = send_movie_genre_mapping_request()['genres']
    tv_genres = send_tv_genre_mapping_request()['genres']

    for genre in movie_genres:
        genre_list.append(genre['name'])

    for genre in tv_genres:
        genre_list.append(genre['name'])

    return genre_list

def filter_on_genre(medias, genre, GENRE_MAP):
    filtered_media = []
    genre_id = GENRE_MAP[genre]

    for media in medias:
        if genre_id in media.genre_ids:
            filtered_media.append(media)

    return filtered_media

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

def ungroup_providers(grouped_providers):
    if grouped_providers is None:
        return None
    providers = map(set, grouped_providers.values())
    providers = reduce(lambda x, y: x.union(y), providers)
    providers = list(providers)
    providers.sort(key=lambda provider: provider.display_priority)
    return providers

def get_trailer(id):
    url = "https://api.themoviedb.org/3/movie/{}/videos?api_key=502ba2adb453be2c9f48a7f5137ba2f4".format(id)
    response = requests.get(url).json()
    response = response['results']
    key = ""
    for item in response:
        if item['official'] == True and item['type'] == 'Trailer' and item['site'] == "YouTube":
            key = item['key']

    youtube = "https://www.youtube.com/embed/{}".format(key)
    return youtube



def to_image_path(filename, size):
    if filename is not None:
        return urljoin(f'{TMDB_IMG_BASE_URL}', f'{size}/{filename.lstrip("/")}')
    else:
        return None
