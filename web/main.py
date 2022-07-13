"""
This is the Quality OpenAPI web application which offers a user interface to query Quality metadata information of datasets.

- main.py: The starting point.
- routes\\\\rt_web.py: Routes module handling all HTML end points
- static\\\\: Website JavaScript and CSS code
- templates\\\\: Website HTML pages templates
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
from flask_wtf.csrf import CSRFProtect
from flask_babel import Babel, lazy_gettext as gettext, _

# Application imports
from routes import *


# Create the Flask application
app = Flask(__name__)

# Flask Configurations
app.config['JWT_TOKEN_LOCATION'] = ["cookies"]
app.config['JWT_ACCESS_COOKIE_NAME'] = config.TOKEN_COOKIE_NAME
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(minutes=config.TOKEN_EXP_MINUTES)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = datetime.timedelta(minutes=config.TOKEN_REFRESH_EXP_MINUTES)
app.config['SECRET_KEY'] = config.TOKEN_KEY_WEB  # For Web auth and CSRF

# Trick to support accented characters!
# After further tests, it seems the accented characters are only lost when the response is returned inside a browser.
# Requests via Postman already work with accents even when True. Anyways, doesn't hurt to leave it False for all.
app.config['JSON_AS_ASCII'] = False

# Create a Flask JWT Manager
jwtMan = JWTManager(app)

# Babel
babel = Babel(app)
app.config['BABEL_TRANSLATION_DIRECTORIES'] = './translations'
app.config["BABEL_DEFAULT_LOCALE"] = "en"

# Register the WEB routes blueprint in Flask
app.register_blueprint(routes)

# Register the CSRF protection
csrf = CSRFProtect(app)

# Read the parameters
app.jinja_env.globals["api_url"] = config.API_URL()


@babel.localeselector
def get_locale():
    return session.get('language', 'en')


@jwtMan.unauthorized_loader
def _handle_token_missing(_reason):
    """
    Handles the returned response when the token is missing.
    """

    print("app_web._handle_token_missing")
    print(_reason)
    return rt_core.redirect_expired()


@jwtMan.invalid_token_loader
def _handle_token_invalid_check(_reason):
    """
    Handles the returned response when the token is invalid.
    """

    print("app_web._handle_token_invalid_check")
    print(_reason)
    return rt_core.redirect_expired()


@jwtMan.expired_token_loader
def _handle_token_expired(_jwt_header, _jwt_data):
    """
    Handles the returned response when the token has expired.
    """

    print("app_web._handle_token_expired")
    return rt_core.redirect_expired()


@app.errorhandler(404)
def _handle_not_found(_reason):
    """
    Handles the returned response when the URL or information wasn't found.
    """

    print("app_web._handle_not_found")
    print(_reason)
    return rt_core.redirect_not_found()


@app.errorhandler(429)
def _handle_rate_limit(rate_limit_exception):
    """
    Handles the returned response when the API is rate limiting a User.
    """

    print("app_web._handle_rate_limit")
    return rt_core.response_user(RateLimitedException(rate_limit_exception.description))


@app.errorhandler(Exception)
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

    # Run
    app.run(host='0.0.0.0', port=8080, debug=config.IS_DEV())
