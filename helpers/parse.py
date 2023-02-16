from dataclasses import dataclass
from enum import Enum

import pycountry

import helpers.tmdb as tmdb

from .model import *

ALL_LOCALES = sorted(list(pycountry.countries), key=lambda country: country.name)

def parse_search_results(results):
    results = map(Media.from_json, results)
    results = filter(lambda media: media is not None, results)      # Removing non-media results.
    results = sorted(results, key=lambda media: -media.popularity)  # Sorting by decreasing popularity.
    return results

def extract_providers(results, locale):
    results = results[locale]

    return {
        MediaAccessMode.SUBSCRIBE.value: map(Provider.from_json, results.get(MediaAccessMode.SUBSCRIBE.value, [])),
        MediaAccessMode.RENT.value: map(Provider.from_json, results.get(MediaAccessMode.RENT.value, [])),
        MediaAccessMode.BUY.value: map(Provider.from_json, results.get(MediaAccessMode.BUY.value, []))
    }
