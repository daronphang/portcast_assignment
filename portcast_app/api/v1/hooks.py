from marshmallow import ValidationError
from flask import current_app, jsonify, g
from . import api_v1
from portcast_app.utils import CustomException, metadata_log


'''
Register errors raised in blueprint 
'''


# library errors
@api_v1.errorhandler(Exception)
def bad_request(e):
    current_app.logger.error(e)
    return jsonify({
        'error': 'bad request',
        'message': str(e),
    }), 400


# schema errors
@api_v1.errorhandler(ValidationError)
def invalid_schema(e):
    current_app.logger.error(e, extra=metadata_log(400, g))
    return jsonify({
        'error': 'invalid schema',
        'message': e.messages
    }), 400


# custom application errors
@api_v1.errorhandler(CustomException)
def app_custom_exception(e):
    current_app.logger.error(e, extra=metadata_log(e.STATUS_CODE, g))
    return jsonify({
        'error': e.__class__.__name__,
        'message': e.message
    }), e.STATUS_CODE