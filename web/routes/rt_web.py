"""
This module, implementing OpenAPI concepts, manages the various routes for the web interface.

End points:
 - / or /en/home or /fr/accueil : endpoing to home page in correct language
 - /en/login or /fr/login : endpoint to a page to login with the API
 - /en/logout or /fr/logout : endpoint to a page to logout with the API
 - /en/query or /fr/query : endpoint to a page to query a quality metadata uuid
 - /en/profile or /fr/profile : endpoint to the user profile page
 - /en/expired or /fr/expired : endpoint to a page indicating the User has expired/invalid credentials
 - /en/denied or /fr/denied : endpoint to a page indicating the User has insufficient permissions
 - /en/not_found or /fr/not_found : endpoint to a page indicating the page originally queried couldn't be found
"""

# 3rd party imports
from flask import request

# Application imports
from core import config, auth
from core.lib.exceptions import *
from . import routes
import core.routes.rt_core as rt_core


@routes.route('/')
@routes.route('/en/home')
def html_index():
    """
    Handles a GET request on "/" end point to load an HTML page for the Home page.
    """

    try:
        return rt_core.render_page('home.html', '/fr/accueil')

    except Exception as err:
        # Weird, just proceed
        print(err)
        return rt_core.render_page('home.html', '/fr/accueil')


@routes.route('/fr/accueil')
def html_index_fr():
    """
    Handles a GET request on "/" end point to load an HTML page for the Home page.
    """

    try:
        return rt_core.render_page('home.html', '/en/home')

    except Exception as err:
        # Weird, just proceed
        print(err)
        return rt_core.render_page('home.html', '/en/home')


@routes.route('/en/login', methods=["GET"])
def html_login():
    """
    Handles a GET request on "/login" end point to load an HTML page with login capabilities for a User.
    """

    try:
        # If not already logged in
        if not auth.current_user():
            return rt_core.render_page('login.html', '/fr/login')

        else:
            # Already logged in
            return rt_core.redirect_home()

    except Exception as err:
        # Weird, just proceed
        print(err)
        return rt_core.render_page('login.html', '/fr/login')


@routes.route('/fr/login', methods=["GET"])
def html_login_fr():
    """
    Handles a GET request on "/fr/login" end point to load an HTML page with login capabilities for a User.
    """

    try:
        # If not already logged in
        if not auth.current_user():
            return rt_core.render_page('login.html', '/en/login')

        else:
            # Already logged in
            return rt_core.redirect_home()

    except Exception as err:
        # Weird, just proceed
        print(err)
        return rt_core.render_page('login.html', '/en/login')


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


@routes.route('/en/add')
#@rt_core.validate_user_html_level(config.ROLE_LEVEL_USER)
def html_upload_quality():
    """
    Handles a GET request on "/upload" end point to show a page with uploading
     Metadata Quality Information capabilities.
    """

    try:
        return rt_core.render_page('add.html', '/fr/add')

    except Exception as err:
        # Weird, just proceed
        print("html_upload_quality")
        print(err)
        return rt_core.redirect_home()


@routes.route('/fr/add')
#@rt_core.validate_user_html_level(config.ROLE_LEVEL_USER)
def html_upload_quality_fr():
    """
    Handles a GET request on "/upload" end point to show a page with uploading
     Metadata Quality Information capabilities.
    """

    try:
        return rt_core.render_page('add.html', '/en/add')

    except Exception as err:
        # Weird, just proceed
        print("html_upload_quality_fr")
        print(err)
        return rt_core.redirect_home()


@routes.route('/profile')
@rt_core.validate_user_html_level(config.ROLE_LEVEL_USER)
def html_my_profile():
    """
    Handles a GET request on "/profile" end point to load an HTML page with information on the user profile.
    """

    try:
        return rt_core.render_page('my_profile.html', '/profile')

    except Exception as err:
        # Weird, just proceed
        print("html_my_profile")
        print(err)
        return rt_core.redirect_home()


@routes.route('/en/logout')
@rt_core.validate_user_html_level(config.ROLE_LEVEL_USER)
def html_logout():
    """
    Handles a GET request on "/logout" end point to load an HTML page indicating the User is being logged out.
    """

    try:
        # Logout the User
        auth.logout()

        # Render logout page
        return rt_core.render_page('basics/logout.html', '/fr/logout')

    except Exception as err:
        # Weird, just proceed
        print(err)
        return rt_core.redirect_home()


@routes.route('/fr/logout')
@rt_core.validate_user_html_level(config.ROLE_LEVEL_USER)
def html_logout_fr():
    """
    Handles a GET request on "/fr/logout" end point to load an HTML page indicating the User is being logged out.
    """

    try:
        # Logout the User
        auth.logout()

        # Render logout page
        return rt_core.render_page('basics/logout.html', '/en/logout')

    except Exception as err:
        # Weird, just proceed
        print(err)
        return rt_core.redirect_home()


@routes.route('/en/expired')
def html_expired():
    """
    Handles a GET request on "/expired" end point to load an HTML page indicating the User token has expired or
     is invalid.
    """

    try:
        return rt_core.render_page('basics/expired.html', '/fr/expired')

    except Exception as err:
        # Weird, just proceed
        print(err)
        return rt_core.redirect_home()


@routes.route('/fr/expired')
def html_expired_fr():
    """
    Handles a GET request on "/fr/expired" end point to load an HTML page indicating the User token has expired or
     is invalid.
    """

    try:
        return rt_core.render_page('basics/expired.html', '/en/expired')

    except Exception as err:
        # Weird, just proceed
        print(err)
        return rt_core.redirect_home()


@routes.route('/en/denied')
def html_denied():
    """
    Handles a GET request on "/denied" end point to load an HTML page indicating the User token has
     insufficient permissions.
    """

    try:
        return rt_core.render_page('basics/denied.html', '/fr/denied')

    except Exception as err:
        # Weird, just proceed
        print(err)
        return rt_core.redirect_home()


@routes.route('/fr/denied')
def html_denied_fr():
    """
    Handles a GET request on "/fr/denied" end point to load an HTML page indicating the User token has
     insufficient permissions.
    """

    try:
        return rt_core.render_page('basics/denied.html', '/en/denied')

    except Exception as err:
        # Weird, just proceed
        print(err)
        return rt_core.redirect_home()


@routes.route('/en/not_found')
def html_not_found():
    """
    Handles a GET request on "/not_found" end point to load an HTML page indicating the Page couldn't be found.
    """

    try:
        return rt_core.render_page('basics/not_found.html', '/fr/not_found')

    except Exception as err:
        # Weird, just proceed
        print(err)
        return rt_core.redirect_home()


@routes.route('/fr/not_found')
def html_not_found_fr():
    """
    Handles a GET request on "/not_found" end point to load an HTML page indicating the Page couldn't be found.
    """

    try:
        return rt_core.render_page('basics/not_found.html', '/en/not_found')

    except Exception as err:
        # Weird, just proceed
        print(err)
        return rt_core.redirect_home()
