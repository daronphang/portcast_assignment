import pytest
from flask import g


def test_get(app, requests_mock):
    url = 'http://metaphorpsum.com/paragraphs/1/50'
    p = 'test get endpoint'

    requests_mock.get(url, text=p)

    client = app.test_client()
    resp = client.get('/api/v1/get')
    assert resp.status_code == 200
    assert resp.get_data(as_text=True) == p


def test_search(app):
    payload = {
        'keywords': ['hello', 'test'],
        'operator': 'AND'
    }

    # requires active app context for db 
    with app.app_context():
        client = app.test_client()
        resp = client.post('/api/v1/search', json=payload)
        assert resp.status_code == 200
        assert 'results' in resp.json

    # test invalid schema
    payload['operator'] = 2

    with app.app_context():
        client = app.test_client()
        resp = client.post('/api/v1/search', json=payload)
        assert resp.status_code == 400
        assert resp.json['error'] == 'invalid schema'


def test_dictionary(app):
    # requires active app context for db 
    with app.app_context():
        client = app.test_client()
        resp = client.get('/api/v1/dictionary', content_type='application/json')
        assert resp.status_code == 200
        assert 'results' in resp.json
