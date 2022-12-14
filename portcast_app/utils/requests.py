import requests
from flask import g, current_app
from functools import wraps


def requests_http(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not hasattr(g, 'requests'):
            g.requests = requests.Session()
        
        # flask extension doc for async
        ensure_sync = getattr(current_app, "ensure_sync", None)
        if ensure_sync is not None:
            return ensure_sync(f)(*args, **kwargs)
        return f(*args, **kwargs)
    return wrapper
