from enum import Enum

from .user import User

class MediaType(Enum):
    MOVIE = 'movie'
    TV = 'tv'

    @classmethod
    def values(cls):
        return [e.value for e in cls]

# TODO: Convert to dataclass.
class Media:
    UNKNOWN_ID = -1
    MAX_CHAR_OVERVIEW = 1000

    def __init__(
        self,
        id,
        title,
        media_type,
        poster_path,
        overview,
        popularity
    ):
        self.id = id
        self.title = title
        self.media_type = media_type
        self.poster_path = poster_path
        self.overview = overview
        self.popularity = popularity

    @staticmethod
    def from_json(json_str, media_type=None):
        from helpers.tmdb import to_image_path      # Don't move outside, leads to circular import.

        if media_type is None:
            # If `media_type` is not explicitly passed, search for it in json.
            if json_str['media_type'] in MediaType.values():
                media_type = MediaType(json_str['media_type'])
            else:
                return None     # Handles `media_type` like 'person', which we don't want.

        return Media(
            int(json_str.get('id', Media.UNKNOWN_ID)),
            json_str.get('name', None) if media_type == MediaType.TV.value else json_str.get('title', None),
            media_type,
            to_image_path(json_str.get('poster_path', None), 'original'),
            json_str.get('overview', None)[:Media.MAX_CHAR_OVERVIEW],
            json_str.get('popularity', 0)
        )

# TODO: Convert to dataclass.
class Provider:
    UNKNOWN_ID = -1

    def __init__(self, id, name, logo_path):
        self.id = id
        self.name = name
        self.logo_path = logo_path

    @staticmethod
    def from_json(json_str):
        from helpers.tmdb import to_image_path

        return Provider(
            json_str.get('provider_id', Provider.UNKNOWN_ID),
            json_str.get('provider_name', 'NA'),
            to_image_path(json_str.get('logo_path', None), 'w92')
        )

class MediaAccessMode(Enum):
    SUBSCRIBE = 'flatrate'
    RENT = 'rent'
    BUY = 'buy'

def get_watchlist(user_id):
    user = User.query.filter_by(id=user_id).first()
    watch_list = []
    for movie in user.movies:
        print(movie.id)
        watch_list.append([movie.path, movie.movie_name])

    return watch_list
