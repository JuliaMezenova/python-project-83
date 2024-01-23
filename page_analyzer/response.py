import requests


def get_response(url):
    try:
        response = requests.get(url, timeout=2)
    except (
        requests.exceptions.RequestException,
        requests.exceptions.Timeout
    ):
        return None
    if response:
        if response.status_code == 200:
            return response
    return None
