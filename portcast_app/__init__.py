from flask import current_app, Flask, jsonify, request, g
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_caching import Cache
from datetime import datetime
import logging
from .config import config_factory
from .utils import metadata_log, init_DB, exponential_backoff, DBFailure


origins = ['*']

cors = CORS()
mm = Marshmallow()
cache = Cache()

'''
Application factory for application package. \
Delays creation of an app by moving it into a factory function that can be \
explicitly invoked from script and apply configuration changes.
'''

def create_app(config):
    app = Flask(__name__)

    # disable WSGI logging
    logging.getLogger('werkzeug').disabled = True

    app.config.from_object(config_factory[config]) # load config from python module
    config_factory[config].init_app(app)

    # Exposes all resources matching /* to CORS and allows Content-Type header
    # For cookies, need implement CSRF as additional security measure
    cors.init_app(app, resources={r"/*": {"origins": origins}})
    mm.init_app(app)
    cache.init_app(app)

    # although docker-compose starts DB first, it does not wait for DB to be ready
    # exponential backoff for resilience
    with app.app_context():
        exponential_backoff(Exception)(init_DB)()
        
 
    from portcast_app.api.v1 import api_v1 as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')

    register_global_errors(app)
    register_global_hooks(app)

    return app


def register_global_hooks(app):

    # @app.before_first_request
    # def initialize():
    #     init_DB()

    @app.before_request
    def set_global_variables():
        g.request_timestamp_start = datetime.utcnow()
        g.context = request.json if request.method == 'POST' else None


    @app.after_request
    def log_request(resp):
        if resp.status_code < 400:
            current_app.logger.info(
                'after request logging',
                extra=metadata_log(resp.status_code, g)
            )
        return resp
    
    @app.teardown_appcontext
    def close_DB(f):
        if hasattr(g, 'mysql_db'):
            g.mysql_db.close()

        if hasattr(g, 'requests'):
            g.requests.close()

        return f



def register_global_errors(app):
    
    @app.errorhandler(400)
    def bad_request(e):
        current_app.logger.error(e)
        return jsonify({
            'error': 'bad request',
            'message': e.description,
        }), 400


    @app.errorhandler(404)
    def endpoint_not_found(e):
        current_app.logger.error(e)
        return jsonify({
            'error': 'resource not found',
            'message': e.description
        }), 404


    @app.errorhandler(500)
    def server_error(e):
        current_app.logger.error(e)
        return jsonify({
            'error': 'server error',
            'message': e.description
        }), 500