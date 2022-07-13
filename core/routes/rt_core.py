"""
This module offers utility functions shared across the application to handle the routes.
"""

# Core modules
from functools import wraps

# 3rd party imports
from flask import request, jsonify, abort, redirect, make_response, render_template, session

# Application modules
from core import config, auth
from core.lib.exceptions import *


def validate_user_level(role_level):
    """
    Decorator function to validate the user access to a given endpoint.
     When the user is denied access, a JSON response is returned.

    :param role_level: The role level the user should have
    :returns: A Flask response which is either the actual decorated function's response or
    an error response handled herein.
    """

    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                # Validate user (throws if fails)
                auth.validate_user(role_level)

                # Go
                return fn(*args, **kwargs)

            except TokenInsufficientException as err:
                return response_user(err)

            except TokenRevokedException as err:
                return response_user(err)

            # except (Exception,):
            #    return redirect_expired()

        # Trick to prevent wrappers from overriding each other..
        wrapper.__name__ = fn.__name__
        return decorator

    return wrapper


def validate_user_html_level(role_level):
    """
    Decorator function to validate the user access to a given endpoint.
     When the user is denied access, they're redirected to another url indicating the problem.

    :param role_level: The role level the user should have
    :returns: A Flask response which is either the actual decorated function's response or
    an error response (a web redirection) handled herein.
    """

    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                # Validate user (throws if fails)
                auth.validate_user(role_level)

                # Go
                return fn(*args, **kwargs)

            except TokenInsufficientException:
                return redirect_denied()

            except TokenRevokedException:
                return redirect_expired()

            # except (Exception,):
            #    return redirect_expired()

        # Trick to prevent wrappers from overriding each other..
        wrapper.__name__ = fn.__name__
        return decorator

    return wrapper


def response_201(body):
    """
    Returns the given body on a 201 response.

    :returns: The given body on a 201 response.
    """

    return make_response(body, 201)


def response_204():
    """
    Returns an empty payload (per standards for a 204).

    :returns: An empty payload (per standards for a 204).
    """

    return make_response("", 204)


def _response(status, title, message, message_fr, cause_exception):
    """
    Creates an official Response Payload which contains an English and French message.

    :param status: The HTTP Status Code for the response. Also the status in the response JSON.
    :param title: The Title in the JSON response
    :param message: The Standard English message in 'detail' property in the JSON response
    :param message_fr: The French message, if any, which is in 'detail_fr' property in the JSON response
    :param cause_exception: The inner exception if any. This will be in a 'dev_cause' property and only when
     application is running in DEV environment.
    :returns: A Flask JSON response indicating a HTTP status and information on the response.
     When running in DEV, the response contains more information.
    """

    # The base payload
    json_res = {
        "status": status,
        "title": title,
        "detail": message
    }

    # If a French message
    if message_fr:
        json_res["detail_fr"] = message_fr

    # If in DEV and there's an inner exception
    if config.IS_DEV() and cause_exception:
        json_res["dev_cause"] = str(cause_exception)

    # Return an official NRCan message
    return make_response(jsonify(json_res), status)


def response_user(user_message_exception):
    """
    Creates an official Response Payload from the given UserMessageException.

    :param user_message_exception: The :class:`~lib.exceptions.UserMessageException` object to respond with.
    :returns: A Flask JSON response indicating a HTTP status and information on the response.
     When running in DEV environment, the response contains more information.
    """

    # Redirect
    return _response(user_message_exception.code,
                     user_message_exception.title,
                     user_message_exception.message,
                     user_message_exception.message_fr,
                     user_message_exception.__cause__)


def response_generic(exception):
    """
    Creates an official Response Payload which handles generic cases. The information returned to the User is a
     generic message "Internal Server Error", however when running the application in DEV environment, more
     informations are loaded in 'dev_details' and 'dev_inner_cause' properties.

    :param exception: The :class:`~Exception` object to respond with.
    :returns: A Flask JSON response indicating a HTTP status and general information on the response.
     When running in DEV, the response contains more information.
    """

    # The base payload
    json_res = {
        "status": 500,
        "title": "Internal Server Error",
        "detail": "Internal error"
    }

    # If in DEV, add more details on error
    if config.IS_DEV():
        if exception:
            print(exception)
            json_res["dev_detail"] = str(exception)

        if exception.__cause__:
            print(str(exception.__cause__))
            json_res["dev_inner_cause"] = str(exception.__cause__)

    # Return an official NRCan message
    return make_response(jsonify(json_res), 500)


def abort_user_message(user_msg_exception):
    """
    This function uses the Flask abort method to return an explicitly User intended error on the request.
     More information on the cause of the error is returned when running in DEV environment.

    :param user_msg_exception: The UserMessageException being handled that should be written in the response.
    :returns: A Flask response which indicates the User message returned to the client.
    """

    # Abort the request using the code and message
    abort(response_user(user_msg_exception))


def abort_error(exception):
    """
    This function uses the Flask abort method to return any kind of exception on the request.
     More information on the cause of the error is returned when running in DEV environment.

    :param exception: The generic Exception being handled that should be written in the response.
    :returns: A Flask response which indicates the message returned to the client.
    """

    # Abort the request using the code and exception
    abort(response_generic(exception))


def redirect_home():
    return redirect("/", code=302)


def get_lang_from_url():
    if "/fr/" in request.url:
        return "fr"
    else:
        return "en"

def redirect_expired():
    return redirect("/" + get_lang_from_url() + "/expired?redirect_uri=" + request.url, code=302)


def redirect_denied():
    return redirect("/" + get_lang_from_url() + "/denied", code=302)


def redirect_not_found():
    return redirect("/" + get_lang_from_url() + "/not_found", code=302)


def render_page(url, **kwargs):
    """
    Renders a web page with the expected common parameters for the user interface, including: user, roles, language.
    This function reads the given url to determine the which language the page should be displayed.
    """

    # Set language for Babel
    session['language'] = get_lang_from_url()

    alt_url = request.path
    if session['language'] == "fr":
        alt_url = alt_url.replace("/fr/", "/en/")
    
    else:
        alt_url = alt_url.replace("/en/", "/fr/")

    # If the english root hoom
    if not alt_url or alt_url == "/":
        alt_url = "/fr/home"

    # Proceed    
    return render_template(url,
                           user=auth.current_user(),
                           roles=config.ROLES,
                           lang=session['language'],
                           alt_url=alt_url,
                           using_connexion=config.USING_CONNEXION_API,
                           **kwargs)
