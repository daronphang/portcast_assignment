import os
from dotenv import load_dotenv
from abc import abstractmethod
from .logger import init_logger


basedir = os.path.abspath(os.path.dirname(__file__))


load_dotenv(os.path.join(basedir, '.env'))
load_dotenv(os.path.join(basedir, 'test.env'))


class Config:
    BASEDIR = basedir
    PROJECT_NAME = 'portcast_app'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'R4nd0MS3cret'

    @staticmethod
    def init_app(app):
        # to customize configuration
        pass


class TestingConfig(Config):
    TESTING = True

    # keys must match with DB connector argument names
    MYSQL = {
        'host': os.environ.get('TESTMYSQLHOST'),
        'user': os.environ.get('TESTMYSQLUSERNAME'),
        'password': os.environ.get('TESTMYSQLPASSWORD'),
        'database': os.environ.get('TESTMYSQLDATABASE'),
        # 'unix_socket': os.environ.get('MYSQLUNIXSOCKET'),
        'port': os.environ.get('TESTMYSQLPORT'),
        'pool_name': 'mysql_pool',
        'pool_size': 5,
        'pool_reset_session': True,
    }

    @classmethod
    @abstractmethod
    def init_app(cls, app):
        Config.init_app(app)
        init_logger('TESTING', os.path.join(cls.BASEDIR, cls.PROJECT_NAME))


class DevelopmentConfig(Config):

    # keys must match with DB connector argument names
    MYSQL = {
        'host': os.environ.get('MYSQLHOST'),
        'user': os.environ.get('MYSQLUSERNAME'),
        'password': os.environ.get('MYSQLPASSWORD'),
        'database': os.environ.get('MYSQLDATABASE'),
        # 'unix_socket': os.environ.get('MYSQLUNIXSOCKET'),
        'port': os.environ.get('MYSQLPORT'),
        'pool_name': 'mysql_pool',
        'pool_size': 5,
        'pool_reset_session': True,
    }

    @classmethod
    @abstractmethod
    def init_app(cls, app):
        Config.init_app(app)
        init_logger('TESTING', os.path.join(cls.BASEDIR, cls.PROJECT_NAME))


class ProductionConfig(Config):
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        init_logger('PRODUCTION', os.path.join(cls.BASEDIR, cls.PROJECT_NAME))


config_factory = {
    'TESTING': TestingConfig,
    'PRODUCTION': ProductionConfig,
    'DEFAULT': DevelopmentConfig
}
