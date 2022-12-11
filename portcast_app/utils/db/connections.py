import logging
import mysql.connector as mysql
from flask import current_app, g
from functools import wraps
from ..custom_exc import InvalidField


logger = logging.getLogger(__name__)

'''
Global DB instances, not accessible to other modules except via helper functions
'''
_MySQLDB = None


def init_DB():
    # need to push app_context for app factory method
    global _MySQLDB
    if _MySQLDB is None:
        _MySQLDB = MySQLSession(current_app.config['MYSQL'])


def get_DB(db: str):
    if db == 'MYSQL':
        if not hasattr(g, 'mysql_db'):
            g.mysql_db = _MySQLDB.get_connection()
        return g.mysql_db
    raise InvalidField(f'{db} instance provided is invalid')


'''
Wrapper used as a decorator with class methods when interacting with any database
Ensures cursor.commit() and cursor.close() are closed after DB request
Connection remains open during the lifetime of application/request context
'''
def db_transact(f):
    @wraps(f)
    def wrapper(self, conn, *args, **kwargs):
        try:
            results = f(self, conn, *args, **kwargs)
            conn.commit()
            return results
        except Exception as exc:
            conn.rollback()
            logger.error(f'failed DB transaction: {str(exc)}')
            raise exc
    return wrapper


class MySQLSession:

    def __init__(self, config: dict):
        self._conn_pool = mysql.pooling.MySQLConnectionPool(**config)
    
    def get_connection(self):
        return self._conn_pool.get_connection()


