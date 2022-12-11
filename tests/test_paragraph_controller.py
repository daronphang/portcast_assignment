import pytest
import requests
import aiohttp
import asyncio
from aioresponses import aioresponses
from aiohttp import web
from portcast_app.controllers import Paragraph
from portcast_app.utils import BadRequest


def test_fetch_paragraph(requests_mock):
    url = 'http://metaphorpsum.com/paragraphs/1/50'
    with requests.Session() as s:
        requests_mock.get(url, text='hello world')
        assert Paragraph().fetch_paragraph(s) == 'hello world'


def test_get_unique_keywords():
    p = 'hello* world#, my2 name is1 456 John, 123 this is my world..'
    unique_kw = list(Paragraph().get_unique_keywords(p))
    unique_kw.sort()

    assert unique_kw == [
        'hello',
        'is',
        'john',
        'my',
        'name',
        'this',
        'world',
        ]


def test_get_builder(get_db, requests_mock):
    mysql_db = get_db
    conn = mysql_db.get_connection()

    p1 = 'hello world, my name is John Keller.'
    p2 = 'hello world, my name was Kelly Wilson.'
    p3 = 'hello world my name are awesome'
    p4 = 'hello world my test testing tester'
    p5 = 'hello world she they'
    p6 = 'hello a b c'

    url = 'http://metaphorpsum.com/paragraphs/1/50'
    
    s = requests.Session()

    p = Paragraph()

    with conn:
        # add first paragraph
        requests_mock.get(url, text=p1)
        result = p.get_builder(conn, s)
        assert result == p1

        # no duplicates allowed
        with pytest.raises(BadRequest) as exc:
            p.get_builder(conn, s)
        assert str(exc.value) == 'no duplicate paragraphs allowed'
       
        # # add second paragraph
        requests_mock.get(url, text=p2)
        result = p.get_builder(conn, s)
        assert result == p2

        requests_mock.get(url, text=p3)
        result =p.get_builder(conn, s)
        assert result == p3

        requests_mock.get(url, text=p4)
        result = p.get_builder(conn, s)
        assert result == p4

        requests_mock.get(url, text=p5)
        result = p.get_builder(conn, s)
        assert result == p5

        requests_mock.get(url, text=p6)
        result = p.get_builder(conn, s)
        assert result == p6

    s.close()


def test_search_keywords(get_db):
    mysql_db = get_db
    conn = mysql_db.get_connection()

    p = Paragraph()

    with conn:
        # testing AND operator
        payload = {
            'keywords': ['hello','john'],
            'operator': 'AND'
        }
        results = p.search_with_keywords(conn, payload)
        assert len(results) == 1
        assert results[0] == 'hello world, my name is John Keller.'

        # testing OR operator
        payload = {
            'keywords': ['hello','john'],
            'operator': 'OR'
        }
        results = p.search_with_keywords(conn, payload)
        assert len(results) == 6

        # testing no results
        payload = {
            'keywords': ['hello', 'john', 'wilson'],
            'operator': 'AND'
        }
        results = p.search_with_keywords(conn, payload)
        assert len(results) == 0


def test_get_top_keywords(get_db):
    mysql_db = get_db
    conn = mysql_db.get_connection()

    with conn:
        assert Paragraph().fetch_top_keywords(conn, 4)  == [
            'hello',
            'world',
            'my',
            'name',
            ]


@pytest.mark.asyncio
async def test_fetch_definition_async():
    s = aiohttp.ClientSession()
    kw = 'hello'
    payload = [{
        'meanings': [{
            'definitions': [{
                'definition': 'hello world'
            }]
        }]
    }]

    with aioresponses() as m:
        m.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{kw}', payload=payload)
        resp = await Paragraph().fetch_definition(s, kw)
        assert 'definition' in resp
        assert resp['definition'] == 'hello world'



