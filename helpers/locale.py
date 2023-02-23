from geopy import Nominatim

def coordsToLocale(coords):
    geolocator = Nominatim(user_agent='universal-streaming-search')
    return geolocator.reverse(coords).raw['address']['country_code'].upper()

def ipToLocale(ip):
    return 'AF'
