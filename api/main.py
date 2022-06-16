"""
This is the Clip Zip Ship Admin OpenAPI which offers functions to manage the collections
This API uses Python, Flask, connexion, JWT and psycopg2 frameworks along with the openapi.yaml file.
Navigate to http://{HOST}:{PORT}/ui to visualize the OpenAPI user interface to learn/test this API.

- openapi.yaml: Declares the OpenAPI definition of this application.
- main.py: The starting point.
- routes\\\\rt_api.py: Routes module handling all API end points.
- requirements.txt: Details the Python packages necessary to run this application.
- nginx.conf: The configuration file used when deploying to NGINX. The rate limit for this API is defined in that file.
- uwsgi.ini: The configuration file used when the Python web services are deployed using Web Server Gateway Interface principles.
"""

# Core modules
import sys, os, datetime

# Add the parent folder to the path so that the "core" module can be loaded
sys.path.append(os.path.dirname(sys.path[0]))

# 3rd party imports
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Application imports
from routes import *

# If using Connexion API
app = None
if config.USING_CONNEXION_API:
    # Create the Connexion application to contain the Flask application
    import connexion

    app = connexion.FlaskApp(__name__, specification_dir='./')
    flaskApp = app.app

else:
    # Create the Flask application
    flaskApp = Flask(__name__)

# Flask Configurations
flaskApp.config['JWT_TOKEN_LOCATION'] = ["headers"]  # API working with headers only
flaskApp.config['JWT_COOKIE_CSRF_PROTECT'] = False  # No need, not using cookies, only headers
flaskApp.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(minutes=config.TOKEN_EXP_MINUTES)
flaskApp.config["JWT_REFRESH_TOKEN_EXPIRES"] = datetime.timedelta(minutes=config.TOKEN_REFRESH_EXP_MINUTES)
flaskApp.config['SECRET_KEY'] = config.TOKEN_KEY_API

# Trick to support accented characters!
# After further tests, it seems the accented characters are only lost when the response is returned inside a browser.
# Requests via Postman already work with accents even when True. Anyways, doesn't hurt to leave it False for all.
flaskApp.config['JSON_AS_ASCII'] = False

# Create a Flask JWT Manager
jwtMan = JWTManager(flaskApp)

# If using Connexion API
if config.USING_CONNEXION_API:
    # Read the openapi.yaml file to read specs and configure the endpoints
    app.add_api('openapi.yaml', validate_responses=True)

# Register the API routes blueprint in Flask
flaskApp.register_blueprint(routes)

# Register for CORS
CORS(flaskApp, resources={r"/api/*": {"origins": "*"}})

with flaskApp.app_context():
    """
    Init config
    """
    pass


@jwtMan.unauthorized_loader
def _handle_token_missing(_reason):
    """
    Handles the returned response when the token is missing.
    """

    print("app._handle_token_missing")
    print(_reason)
    return rt_core.response_user(TokenMissingException())


@jwtMan.invalid_token_loader
def _handle_token_invalid_check(_reason):
    """
    Handles the returned response when the token is invalid.
    """

    print("app._handle_token_invalid_check")
    print(_reason)
    return rt_core.response_user(TokenInvalidException())


@jwtMan.expired_token_loader
def _handle_token_expired(_jwt_header, _jwt_data):
    """
    Handles the returned response when the token has expired.
    """

    print("app._handle_token_expired")
    return rt_core.response_user(TokenExpiredException())


@flaskApp.errorhandler(404)
def _handle_not_found(_reason):
    """
    Handles the returned response when the URL or information wasn't found.
    """

    print("app._handle_not_found")
    print(_reason)
    return rt_core.response_user(NotFoundException())


@flaskApp.errorhandler(405)
def _handle_method_not_allowed(_reason):
    """
    Handles the returned response when the HTTP Method wasn't allowed.
    """

    print("app._handle_method_not_allowed")
    print(_reason)
    return rt_core.response_user(MethodNotAllowedException())


@flaskApp.errorhandler(429)
def _handle_rate_limit(rate_limit_exception):
    """
    Handles the returned response when the API is rate limiting a User.
    """

    print("app._handle_rate_limit")
    return rt_core.response_user(RateLimitedException(rate_limit_exception.description))


@flaskApp.errorhandler(Exception)
def _handle_all_errors(err):
    """
    Handles any exception.
    """

    print("app._handle_all_errors")
    return rt_core.response_generic(err)


# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    """
    Run!
    """

    # If using Connexion API
    if config.USING_CONNEXION_API:
        app.run(host='0.0.0.0', port=5001, debug=config.IS_DEV())

    else:
        flaskApp.run(host='0.0.0.0', port=5001, debug=config.IS_DEV())
