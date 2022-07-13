"""
This module, implementing OpenAPI concepts, manages the various routes for the web interface.

End points:
 - / or /en/home or /fr/home : endpoing to home page in correct language
 - /en/login or /fr/login : endpoint to a page to login with the API
 - /en/logout or /fr/logout : endpoint to a page to logout with the API
 - /en/query or /fr/query : endpoint to a page to query a quality metadata uuid
 - /en/profile or /fr/profile : endpoint to the user profile page
 - /en/expired or /fr/expired : endpoint to a page indicating the User has expired/invalid credentials
 - /en/denied or /fr/denied : endpoint to a page indicating the User has insufficient permissions
 - /en/not_found or /fr/not_found : endpoint to a page indicating the page originally queried couldn't be found
"""

# 3rd party imports
from flask import request, session

# Application imports
from core import config, auth, clip_zip_ship
from core.lib.exceptions import *
from . import routes
import core.routes.rt_core as rt_core


@routes.route('/')
@routes.route('/<any(en,fr):lang>/home')
def html_index(lang = "en"):
    """
    Handles a GET request on "/" or "/<lang>/home" end point to load an HTML page for the Home page.
    """

    try:
        return rt_core.render_page('home.html')

    except Exception as err:
        # Weird, just proceed
        print(err)
        return rt_core.render_page('home.html')


@routes.route('/<any(en,fr):lang>/login', methods=["GET"])
def html_login(lang):
    """
    Handles a GET request on "/<lang>/login" end point to load an HTML page with login capabilities for a User.
    """

    try:
        # If not already logged in
        if not auth.current_user():
            return rt_core.render_page('login.html')

        else:
            # Already logged in
            return rt_core.redirect_home()

    except Exception as err:
        # Weird, just proceed
        print(err)
        return rt_core.render_page('login.html')


@routes.route('/<any(en,fr):lang>/add')
@rt_core.validate_user_html_level(config.ROLE_LEVEL_USER)
def html_upload_quality(lang):
    """
    Handles a GET request on "/<lang>/add" end point to show a page with uploading
     Metadata Quality Information capabilities.
    """

    try:
        return rt_core.render_page('add.html', parents=clip_zip_ship.get_parents())

    except Exception as err:
        # Weird, just proceed
        print(err)
        return rt_core.redirect_home()


@routes.route('/<any(en,fr):lang>/logout')
@rt_core.validate_user_html_level(config.ROLE_LEVEL_USER)
def html_logout(lang):
    """
    Handles a GET request on "/<lang>/logout" end point to load an HTML page indicating the User is being logged out.
    """

    try:
        # Logout the User
        auth.logout()

        # Render logout page
        return rt_core.render_page('basics/logout.html')

    except Exception as err:
        # Weird, just proceed
        print(err)
        return rt_core.redirect_home()


@routes.route('/<any(en,fr):lang>/expired')
def html_expired(lang):
    """
    Handles a GET request on "/<lang>/expired" end point to load an HTML page indicating the User token has expired or
     is invalid.
    """

    try:
        return rt_core.render_page('basics/expired.html')

    except Exception as err:
        # Weird, just proceed
        print(err)
        return rt_core.redirect_home()


@routes.route('/<any(en,fr):lang>/denied')
def html_denied(lang):
    """
    Handles a GET request on "/<lang>/denied" end point to load an HTML page indicating the User token has
     insufficient permissions.
    """

    try:
        return rt_core.render_page('basics/denied.html')

    except Exception as err:
        # Weird, just proceed
        print(err)
        return rt_core.redirect_home()


@routes.route('/<any(en,fr):lang>/not_found')
def html_not_found(lang):
    """
    Handles a GET request on "/<lang>/not_found" end point to load an HTML page indicating the Page couldn't be found.
    """

    try:
        return rt_core.render_page('basics/not_found.html')

    except Exception as err:
        # Weird, just proceed
        print(err)
        return rt_core.redirect_home()


@routes.route('/login', methods=["POST"])
def html_login_post():
    """
    Handles a POST request on "/login" end point to authenticate a User with a username and password.
    """

    try:
        body = request.json
        if "username" in body and "password" in body:
            # Redirect
            return auth.generate_token(body["username"], body["password"])

        else:
            # Parameters invalid
            raise ParametersInvalidException()

    except UserMessageException as err:
        # Handle the error for the User
        rt_core.abort_user_message(err)

    except Exception as err:
        # Raise a generic error
        rt_core.abort_error(err)


@routes.route('/profile')
@rt_core.validate_user_html_level(config.ROLE_LEVEL_USER)
def html_my_profile():
    """
    Handles a GET request on "/profile" end point to load an HTML page with information on the user profile.
    """

    try:
        return rt_core.render_page('my_profile.html')

    except Exception as err:
        # Weird, just proceed
        print("html_my_profile")
        print(err)
        return rt_core.redirect_home()


