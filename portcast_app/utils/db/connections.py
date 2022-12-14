import logging
import mysql.connector as mysql_conn
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


def mysql(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not hasattr(g, 'mysql_db'):
            g.mysql_db = _MySQLDB.get_connection()
        
        # flask extension doc for async
        ensure_sync = getattr(current_app, "ensure_sync", None)
        if ensure_sync is not None:
            return ensure_sync(f)(*args, **kwargs)
        return f(*args, **kwargs)
    return wrapper


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
        self._conn_pool = mysql_conn.pooling.MySQLConnectionPool(**config)
    
    def get_connection(self):
        return self._conn_pool.get_connection()


