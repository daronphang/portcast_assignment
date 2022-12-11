import re
import uuid
from .sql_metadata import sql_metadata
from portcast_app.utils import (
    SqlHelper,
    BadRequest,
    db_transact
)


'''
Assumptions:
- paragraphs do not contain other characters other than [A-Za-z.,]
- i.e. no numbers, quotes, special characters
- each valid word is separated with space
'''

class Paragraph:

    def fetch_paragraph(self, s):
        with s.get('http://metaphorpsum.com/paragraphs/1/50') as resp:
            # fetch 1 paragraph, 50 lines
            resp.raise_for_status()
        return resp.text


    def get_unique_keywords(self, paragraph):
        unique_kw = set()
        words = paragraph.split(' ')
        for word in words:
            word = re.search('^[a-z\']+', word.lower())
            if word:
                unique_kw.add(word.group(0))
        return unique_kw


    def add_new_paragraph(self, cursor, paragraph):
        # insert paragraph if not duplicate
        uid = uuid.uuid4().hex
        payload = {
            'uid': uid,
            'paragraph': paragraph
        }
        SqlHelper()\
            .replace(sql_metadata['ADD_NEW_PARAGRAPH'], payload)\
                .query(cursor)
        if cursor.rowcount == 0:
            raise BadRequest('no duplicate paragraphs allowed')
        return uid
   

    def add_unique_keywords(self, cursor, uid, unique_kw):
        # insert unique keywords to database
        entries = list(
            map(lambda kw: {'keyword': kw, 'paragraph_uid': uid}, unique_kw)
            )
        SqlHelper()\
            .generate_insert(
                'metaphorpsum_unique_keywords',
                entries
                ).query(cursor)


    @db_transact
    def search_with_keywords(self, conn, payload):
        cursor = conn.cursor(dictionary=True)
        sql_helper = SqlHelper()
        cursor.execute('DROP TABLE IF EXISTS temp')
        sql_helper\
            .replace(
                sql_metadata['SEARCH_KEYWORDS_TEMP'],
                {'keywords': payload['keywords']}
            ).query(cursor)
        sql_helper\
            .replace(
                sql_metadata['SEARCH_KEYWORDS'], 
                {'count': len(payload['keywords']) if payload['operator'] == 'AND' else 1}
            ).query(cursor)
        return [x['paragraph'] for x in cursor.fetchall()]
    

    @db_transact
    def fetch_top_keywords(self, conn, limit):
        cursor = conn.cursor(dictionary=True)
        payload = {'limit': limit}
        SqlHelper()\
            .replace(sql_metadata['FETCH_TOP_KEYWORDS'], payload)\
                .query(cursor)
        return [x['keyword'] for x in cursor.fetchall()]


    async def fetch_definition(self, s, keyword: str):
        try:
            async with s.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{keyword}') as resp:
                result = await resp.json()
                
                # check if there are no definitions found
                if isinstance(result, dict) \
                    and 'title' in result \
                        and result['title'].upper() == 'NO DEFINITIONS FOUND':
                        definition = 'no definitions found'
                elif isinstance(result, list):
                    # returning first definition
                    definition = result[0]['meanings'][0]['definitions'][0]['definition']
                else:
                    definition = 'unknown error occurred while fetching'
            return {
                'word': keyword,
                'definition': definition
            }
        except Exception as e:
            raise BadRequest(str(e))
    

    @db_transact
    def get_builder(self, conn, s):
        cursor = conn.cursor(dictionary=True)
        paragraph = self.fetch_paragraph(s)
        unique_kw = self.get_unique_keywords(paragraph)
        uid = self.add_new_paragraph(cursor, paragraph)
        self.add_unique_keywords(cursor, uid, unique_kw)
        return paragraph
