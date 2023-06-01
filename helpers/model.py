from enum import Enum
import pycountry

ALL_LOCALES = sorted(list(pycountry.countries), key=lambda country: country.name)
ALL_LANGUAGES_MAP = {'ab': 'Abkhaz', 'aa': 'Afar', 'af': 'Afrikaans', 'ak': 'Akan', 'sq': 'Albanian', 'am': 'Amharic', 'ar': 'Arabic', 'an': 'Aragonese', 'hy': 'Armenian', 'as': 'Assamese', 'av': 'Avaric', 'ae': 'Avestan', 'ay': 'Aymara', 'az': 'Azerbaijani', 'bm': 'Bambara', 'ba': 'Bashkir', 'eu': 'Basque', 'be': 'Belarusian', 'bn': 'Bengali', 'bh': 'Bihari', 'bi': 'Bislama', 'bs': 'Bosnian', 'br': 'Breton', 'bg': 'Bulgarian', 'my': 'Burmese', 'ca': 'Catalan; Valencian', 'ch': 'Chamorro', 'ce': 'Chechen', 'ny': 'Chichewa; Chewa; Nyanja', 'zh': 'Chinese', 'cn': 'Chinese', 'cv': 'Chuvash', 'kw': 'Cornish', 'co': 'Corsican', 'cr': 'Cree', 'hr': 'Croatian', 'cs': 'Czech', 'da': 'Danish', 'dv': 'Divehi; Maldivian;', 'nl': 'Dutch', 'dz': 'Dzongkha', 'en': 'English', 'eo': 'Esperanto', 'et': 'Estonian', 'ee': 'Ewe', 'fo': 'Faroese', 'fj': 'Fijian', 'fi': 'Finnish', 'fr': 'French', 'ff': 'Fula', 'gl': 'Galician', 'ka': 'Georgian', 'de': 'German', 'el': 'Greek, Modern', 'gn': 'Guaraní', 'gu': 'Gujarati', 'ht': 'Haitian', 'ha': 'Hausa', 'he': 'Hebrew (modern)', 'hz': 'Herero', 'hi': 'Hindi', 'ho': 'Hiri Motu', 'hu': 'Hungarian', 'ia': 'Interlingua', 'id': 'Indonesian', 'ie': 'Interlingue', 'ga': 'Irish', 'ig': 'Igbo', 'ik': 'Inupiaq', 'io': 'Ido', 'is': 'Icelandic', 'it': 'Italian', 'iu': 'Inuktitut', 'ja': 'Japanese', 'jv': 'Javanese', 'kl': 'Kalaallisut', 'kn': 'Kannada', 'kr': 'Kanuri', 'ks': 'Kashmiri', 'kk': 'Kazakh', 'km': 'Khmer', 'ki': 'Kikuyu, Gikuyu', 'rw': 'Kinyarwanda', 'ky': 'Kirghiz, Kyrgyz', 'kv': 'Komi', 'kg': 'Kongo', 'ko': 'Korean', 'ku': 'Kurdish', 'kj': 'Kwanyama, Kuanyama', 'la': 'Latin', 'lb': 'Luxembourgish', 'lg': 'Luganda', 'li': 'Limburgish', 'ln': 'Lingala', 'lo': 'Lao', 'lt': 'Lithuanian', 'lu': 'Luba-Katanga', 'lv': 'Latvian', 'gv': 'Manx', 'mk': 'Macedonian', 'mg': 'Malagasy', 'ms': 'Malay', 'ml': 'Malayalam', 'mt': 'Maltese', 'mi': 'Māori', 'mr': 'Marathi (Marāṭhī)', 'mh': 'Marshallese', 'mn': 'Mongolian', 'na': 'Nauru', 'nv': 'Navajo, Navaho', 'nb': 'Norwegian Bokmål', 'nd': 'North Ndebele', 'ne': 'Nepali', 'ng': 'Ndonga', 'nn': 'Norwegian Nynorsk', 'no': 'Norwegian', 'ii': 'Nuosu', 'nr': 'South Ndebele', 'oc': 'Occitan', 'oj': 'Ojibwe, Ojibwa', 'cu': 'Old Church Slavonic', 'om': 'Oromo', 'or': 'Oriya', 'os': 'Ossetian, Ossetic', 'pa': 'Panjabi, Punjabi', 'pi': 'Pāli', 'fa': 'Persian', 'pl': 'Polish', 'ps': 'Pashto, Pushto', 'pt': 'Portuguese', 'qu': 'Quechua', 'rm': 'Romansh', 'rn': 'Kirundi', 'ro': 'Romanian, Moldavan', 'ru': 'Russian', 'sa': 'Sanskrit (Saṁskṛta)', 'sc': 'Sardinian', 'sd': 'Sindhi', 'se': 'Northern Sami', 'sm': 'Samoan', 'sg': 'Sango', 'sr': 'Serbian', 'gd': 'Scottish Gaelic', 'sn': 'Shona', 'si': 'Sinhala, Sinhalese', 'sk': 'Slovak', 'sl': 'Slovene', 'so': 'Somali', 'st': 'Southern Sotho', 'es': 'Spanish; Castilian', 'su': 'Sundanese', 'sw': 'Swahili', 'ss': 'Swati', 'sv': 'Swedish', 'ta': 'Tamil', 'te': 'Telugu', 'tg': 'Tajik', 'th': 'Thai', 'ti': 'Tigrinya', 'bo': 'Tibetan', 'tk': 'Turkmen', 'tl': 'Tagalog', 'tn': 'Tswana', 'to': 'Tonga', 'tr': 'Turkish', 'ts': 'Tsonga', 'tt': 'Tatar', 'tw': 'Twi', 'ty': 'Tahitian', 'ug': 'Uighur, Uyghur', 'uk': 'Ukrainian', 'ur': 'Urdu', 'uz': 'Uzbek', 've': 'Venda', 'vi': 'Vietnamese', 'vo': 'Volapük', 'wa': 'Walloon', 'cy': 'Welsh', 'wo': 'Wolof', 'fy': 'Western Frisian', 'xh': 'Xhosa', 'yi': 'Yiddish', 'yo': 'Yoruba', 'za': 'Zhuang, Chuang', 'zu': 'Zulu'}

class MediaType(Enum):
    MOVIE = 'movie'
    TV = 'tv'

    @classmethod
    def values(cls):
        return [e.value for e in cls]

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
        popularity,
        genre_ids,
        original_language
    ):
        self.id = id
        self.title = title
        self.media_type = media_type
        self.poster_path = poster_path
        self.overview = overview
        self.popularity = popularity
        self.genre_ids = genre_ids
        self.original_language = original_language

    def __hash__(self):
        return hash(id)

    def __eq__(self, other):
        return (self.id == other.id) and (self.media_type == other.media_type)

    @staticmethod
    def from_json(json_str, media_type=None):
        from helpers.tmdb import \
            to_image_path  # Don't move outside, leads to circular import.

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
            json_str.get('overview', None),
            json_str.get('popularity', 0),
            json_str.get('genre_ids', []),
            json_str.get('original_language', None)
        )

    def __str__(self):
        return f'{self.__class__.__name__}({self.id}, \"{self.title}\", {self.media_type})'

class Provider:
    UNKNOWN_ID = -1

    def __init__(self, id, name, logo_path, display_priority):
        self.id = id
        self.name = name
        self.logo_path = logo_path
        self.display_priority = display_priority

    def __hash__(self):
        return hash(id)

    def __eq__(self, other):
        return self.id == other.id

    @staticmethod
    def from_json(json_str):
        from helpers.tmdb import to_image_path

        return Provider(
            json_str.get('provider_id', Provider.UNKNOWN_ID),
            json_str.get('provider_name', 'NA'),
            to_image_path(json_str.get('logo_path', None), 'original'),
            json_str.get('display_priority', float('inf'))
        )

    def __str__(self):
        return f'{self.__class__.__name__}({self.id}, \"{self.name}\")'

class MediaAccessMode(Enum):
    SUBSCRIBE = 'flatrate'
    RENT = 'rent'
    BUY = 'buy'
