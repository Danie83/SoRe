from django.conf import settings
import requests
import json

def create_auth_url():
    auth_url = f'https://accounts.google.com/o/oauth2/auth?client_id={settings.GOOGLE_CLIENT_ID}&redirect_uri={settings.GOOGLE_REDIRECT_URI}&scope=email&response_type=code'
    return auth_url

def authorize(code):
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        'code': code,
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
        'redirect_uri': settings.GOOGLE_REDIRECT_URI,
        'grant_type': 'authorization_code',
    }
    response = requests.post(token_url, data=data)
    tokens = json.loads(response.text)
    access_token = tokens['access_token']

    user_info_url = f"https://www.googleapis.com/oauth2/v1/userinfo?alt=json&access_token={access_token}"
    response = requests.get(user_info_url)
    user_data = json.loads(response.text)

    return user_data