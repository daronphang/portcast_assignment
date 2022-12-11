sql_metadata = {
    'ADD_NEW_PARAGRAPH': {
        'prep_stmt': '''
            INSERT INTO
            metaphorpsum_paragraphs
            (uid, paragraph)
            SELECT {0} AS uid, {1} AS paragraph
            WHERE NOT EXISTS (
                SELECT
                1
                FROM
                metaphorpsum_paragraphs
                WHERE 
                paragraph = {1}
            )
            ''',
        'sql_helper': ['uid', 'paragraph'],
    },
    'FETCH_TOP_KEYWORDS': {
        'prep_stmt': '''
            SELECT
            keyword,
            COUNT(keyword) AS kw_count
            FROM
            metaphorpsum_unique_keywords
            GROUP BY keyword
            ORDER BY kw_count DESC
            LIMIT {0};
            ''',
        'sql_helper': ['limit']
    },
    'SEARCH_KEYWORDS_TEMP': {
        'prep_stmt': '''
            CREATE TEMPORARY TABLE
            temp
            SELECT
            paragraph_uid,
            COUNT(paragraph_uid) AS p_count
            FROM 
            metaphorpsum_unique_keywords
            WHERE
            keyword IN ({0})
            GROUP BY paragraph_uid     
            ''',
        'sql_helper': ['keywords']
    },
    'SEARCH_KEYWORDS': {
        'prep_stmt': '''
            SELECT
            paragraph
            FROM
            metaphorpsum_paragraphs
            WHERE
            uid IN (
                SELECT
                paragraph_uid
                FROM
                temp
                WHERE
                p_count >= {0}
            );           
            ''',
        'sql_helper': ['count']
    }
}