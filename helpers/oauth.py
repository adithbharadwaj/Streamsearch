import requests
from oauthlib.oauth2 import WebApplicationClient

GOOGLE_CLIENT_ID = '518130499467-b1evb46av5elju33ncr0fd8o37n8v2tc.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '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'
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

client = WebApplicationClient(GOOGLE_CLIENT_ID)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()