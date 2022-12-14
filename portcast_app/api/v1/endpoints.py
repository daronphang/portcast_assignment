import aiohttp
import asyncio
from flask import current_app, g, jsonify
from . import api_v1
from portcast_app import cache
from portcast_app.utils import mysql, requests_http
from portcast_app.schemas import get_request_schema
from portcast_app.controllers import Paragraph

''' 
When using Request or aioHTTP sessions, only one should be used per request
To create the session in view functions
'''


@api_v1.route('/heartbeat', methods=['GET'])
def heartbeat():
    app_name = current_app.config['PROJECT_NAME']
    return jsonify({"message": f'{app_name} is alive'})


@api_v1.route('/get', methods=['GET'])
@mysql
@requests_http
def fetch_paragraph():
    return Paragraph().get_builder(g.mysql_db, g.requests)


@api_v1.route('/search', methods=['POST'])
@mysql
def search_paragraphs():
    payload = get_request_schema('SEARCH').load(g.context)
    results = Paragraph().search_with_keywords(g.mysql_db, payload)
    return jsonify({"results": results})


@api_v1.route('/dictionary', methods=['GET'])
@cache.cached(timeout=60)
@mysql
async def dictionary():
    p = Paragraph()

    keywords = p.fetch_top_keywords(g.mysql_db, 10)

    async with aiohttp.ClientSession() as s:
        tasks = []
        for kw in keywords:
            task = asyncio.create_task(p.fetch_definition(s, kw))
            tasks.append(task)
        results = await asyncio.gather(*tasks)
    return jsonify({"results": results})