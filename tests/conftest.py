import pytest
import os
from dotenv import load_dotenv
from portcast_app import create_app
from portcast_app.utils import MySQLSession

'''
Setup test configurations and store testcases that are used by functions.
'''


load_dotenv(os.path.join(os.pardir, 'portcast_app/test.env'))


_mysql_config = {
    'host': os.environ.get('TESTMYSQLHOST'),
    'user': os.environ.get('TESTMYSQLUSERNAME'),
    'password': os.environ.get('TESTMYSQLPASSWORD'),
    'port': os.environ.get('TESTMYSQLPORT'),
    'pool_name': 'mysql_pool',
    'pool_size': 5,
    'pool_reset_session': True,
    }


@pytest.fixture(scope="session")
def get_db():
    mysql_conf = {**_mysql_config}
    mysql_conf['database'] = os.environ.get('TESTMYSQLDATABASE')
    mysqldb = MySQLSession(mysql_conf)
    yield mysqldb


'''Setup testing database and teardown after all tests have been executed'''
@pytest.fixture(scope='session', autouse=True)
def db_config():
    # create database connections
    mysql_conf = {**_mysql_config}
    mysql_db = MySQLSession(mysql_conf)
    conn = mysql_db.get_connection()

    # create database and tables
    try:
        cursor = conn.cursor()
        cursor.execute('CREATE DATABASE testing_db')
        cursor.execute('USE testing_db')
        sql_str = (
            'CREATE TABLE metaphorpsum_paragraphs ('
            'uid CHAR(32) PRIMARY KEY NOT NULL,'
            'paragraph TEXT NOT NULL,'
            'created_timestamp TIMESTAMP NOT NULL DEFAULT NOW()'
            ') ENGINE=InnoDB'
            )
        cursor.execute(sql_str)
        sql_str = (
            'CREATE TABLE metaphorpsum_unique_keywords ('
            'uid INT PRIMARY KEY NOT NULL AUTO_INCREMENT,'
            'keyword VARCHAR(255) NOT NULL,'
            'paragraph_uid CHAR(32) NOT NULL,'
            'FOREIGN KEY (paragraph_uid) REFERENCES metaphorpsum_paragraphs(uid),'
            'created_timestamp TIMESTAMP NOT NULL DEFAULT NOW()'
            ') ENGINE=InnoDB'
            )
        cursor.execute(sql_str)
        conn.commit()
    except Exception as exc:
        conn.rollback()
    finally:
        conn.close()
    yield 'DATABASE CREATED'

    # teardown database
    conn = mysql_db.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('DROP DATABASE testing_db')
        conn.commit()
    except Exception as exc:
        conn.rollback()
    finally:
        conn.close()


# testing flask app instance
@pytest.fixture()
def app():
    app = create_app('TESTING')

    yield app
