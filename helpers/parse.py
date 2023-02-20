from dataclasses import dataclass
from enum import Enum

import pycountry

import helpers.tmdb as tmdb

from .model import *

ALL_LOCALES = sorted(list(pycountry.countries), key=lambda country: country.name)


def parse_search_results(results):
    results = map(Media.from_json, results)
    results = filter(lambda media: media is not None, results)  # Removing non-media results.
    results = sorted(results, key=lambda media: -media.popularity)  # Sorting by decreasing popularity.
    return results


def extract_providers(results, locale):
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


def filter_on_region(medias, locale_code):
    res = []
    for media in medias:

        temp = tmdb.send_metadata_request(media.id, MediaType(media.media_type.value))['results']
        providers = extract_providers(temp, locale_code)
        if providers is not None:
            res.append(media)

    return res
