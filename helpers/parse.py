from dataclasses import dataclass
from enum import Enum

class MediaType(Enum):
    MOVIE = 'movie'
    TV = 'tv'

    @classmethod
    def values(cls):
        return [e.value for e in cls]

class Media:
    UNKNOWN_ID = -1
    MAX_CHAR_OVERVIEW = 100

    def __init__(
        self,
        id,
        title,
        media_type,
        overview,
        popularity
    ):
        self.id = id
        self.title = title
        self.media_type = media_type
        self.overview = overview
        self.popularity = popularity

    @staticmethod
    def from_json(json_str):
        media_type = json_str['media_type']
        if media_type in MediaType.values():
            return Media(
                int(json_str.get('id', Media.UNKNOWN_ID)),
                json_str.get('name', None) if media_type == MediaType.TV.value else json_str.get('title', None),
                MediaType(media_type),
                json_str.get('overview', None)[:Media.MAX_CHAR_OVERVIEW],
                json_str.get('popularity', 0)
            )
        else:
            return None

class Provider:
    UNKNOWN_ID = -1

    def __init__(self, id, name, logo_path):
        self.id = id
        self.name = name
        self.logo_path = logo_path

    @staticmethod
    def from_json(json_str):
        print(json_str)
        return Provider(
            json_str.get('provider_id', Provider.UNKNOWN_ID),
            json_str.get('provider_name', 'NA'),
            json_str.get('logo_path', None)
        )

class MediaAccessMode(Enum):
    SUBSCRIBE = 'flatrate'
    RENT = 'rent'
    BUY = 'buy'

def parse_search_results(results):
    results = map(Media.from_json, results)
    results = filter(lambda x: x is not None, results)
    return results

def extract_providers(results, locale):
    results = results[locale]

    return {
        MediaAccessMode.SUBSCRIBE.value: map(Provider.from_json, results[MediaAccessMode.SUBSCRIBE.value]),
        MediaAccessMode.RENT.value: map(Provider.from_json, results[MediaAccessMode.RENT.value]),
        MediaAccessMode.BUY.value: map(Provider.from_json, results[MediaAccessMode.BUY.value])
    }
