import requests
from requests.models import HTTPBasicAuth


def fetch_token(url, client_id, client_secret, username, password):
    auth = HTTPBasicAuth(client_id, client_secret)

    response = requests.post(f"{url}/token", auth=auth, data={
        'grant_type': 'password',
        'username': username,
        'password': password
    })

    return response.json()['access_token']