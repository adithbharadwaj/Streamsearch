import pycountry

from helpers.user import User

from .model import *
from .tmdb import send_providers_request

ALL_LOCALES = sorted(list(pycountry.countries), key=lambda country: country.name)

