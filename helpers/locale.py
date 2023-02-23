import ipinfo
from geopy import Nominatim

IPINFO_TOKEN = '7b29c44c2adb5a'

def coordsToLocale(coords):
    geolocator = Nominatim(user_agent='universal-streaming-search')
    return geolocator.reverse(coords).raw['address']['country_code'].upper()

def ipToLocale(ip):
    return ipinfo.getHandler(IPINFO_TOKEN).getDetails(ip).country
