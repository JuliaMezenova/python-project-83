from urllib.parse import urlparse


def normalize(url):
    o = urlparse(url)
    return f'{o.scheme}://{o.netloc}'
