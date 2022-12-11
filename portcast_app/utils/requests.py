import requests
from flask import g


def get_request_session():
    if not hasattr(g, 'requests'):
        g.requests = requests.Session()
    return g.requests
