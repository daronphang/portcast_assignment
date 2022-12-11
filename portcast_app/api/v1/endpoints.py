import aiohttp
import asyncio
from flask import current_app, g, jsonify
from . import api_v1
from portcast_app.utils import get_DB, get_request_session
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
def fetch_paragraph():
    conn = get_DB('MYSQL')
    s = get_request_session()
    
    return Paragraph().get_builder(conn, s)


@api_v1.route('/search', methods=['POST'])
def search_paragraphs():
    payload = get_request_schema('SEARCH').load(g.context)
    conn = get_DB('MYSQL')

    results = Paragraph().search_with_keywords(conn, payload)
    return jsonify({"results": results})


@api_v1.route('/dictionary', methods=['GET'])
async def dictionary():
    conn = get_DB('MYSQL')
    p = Paragraph()

    keywords = p.fetch_top_keywords(conn, 10)

    async with aiohttp.ClientSession() as s:
        tasks = []
        for kw in keywords:
            task = asyncio.create_task(p.fetch_definition(s, kw))
            tasks.append(task)
        results = await asyncio.gather(*tasks)
    return jsonify({"results": results})