from dataclasses import dataclass
from enum import Enum

import pycountry

import helpers.tmdb as tmdb

from .model import *

LOCALES = sorted(list(pycountry.countries), key=lambda country: country.name)

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
