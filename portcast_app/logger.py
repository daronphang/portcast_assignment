import logging
from flask import g, request, has_app_context, has_request_context
from datetime import datetime
from pythonjsonlogger import jsonlogger
from logging.config import dictConfig


class CustomJSONFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJSONFormatter, self).add_fields(log_record, record, message_dict)
        log_record['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if has_app_context():
            log_record['payload'] = g.context if 'context' in g else None
        if has_request_context():
            log_record['correlation_id'] = request.headers.get('X-Correlation-ID')
            log_record['method'] = request.method
            log_record['path'] = request.path


class RequestFormatter(logging.Formatter):
    def format(self, record):
        record.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if has_app_context():
            record.context = g.context
        return super().format(record)


def init_logger(config, file_path):
    if config == 'TESTING':
        handlers = ['wsgi', 'default_fh']
    elif config == 'PRODUCTION':
        handlers = ['rotating_fh_info', 'rotating_fh_err']
    else:
        handlers = ['default_fh']
    
    logging_config = {
        'version': 1,
        "disable_existing_loggers": True,
        'formatters': {
            'default': {
                'format': '%(asctime)s | %(levelname)s | %(module)s | %(message)s'
            },
            'json': {
                '()': CustomJSONFormatter,
                'format': '%(timestamp)s %(levelname)s %(module)s %(correlation_id)s %(path)s %(method)s %(message)s %(payload)s'
            },
            'request': {
                '()': RequestFormatter,
                'format': '%(timestamp)s | %(latency)ss | %(method)s | %(url)s | %(status_code)s | %(levelname)s in %(module)s | %(message)s | %(context)s'
            },
        },
        'root': {
            'level': 'INFO',
            'propagate': False,
            'handlers': handlers
        },
        'handlers': {
            'wsgi': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'stream': 'ext://flask.logging.wsgi_errors_stream',
            },
            'rotating_fh_info': {
                'level': 'INFO',
                'formatter': 'json',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': f'{file_path}-PROD-INFO.log',
                'mode': 'a',
                'maxBytes': 1024000,
                'backupCount': 10,
                'encoding': 'utf-8'
            },
            'rotating_fh_err': {
                'level': 'ERROR',
                'formatter': 'json',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': f'{file_path}-PROD-ERROR.log',
                'mode': 'a',
                'maxBytes': 1024000,
                'backupCount': 10,
                'encoding': 'utf-8'
            },
            'default_fh': {
                'level': 'INFO',
                'formatter': 'json',
                'class': 'logging.FileHandler',
                'filename': f'{file_path}-TESTING.log'
            },
        },
    }
    dictConfig(logging_config)