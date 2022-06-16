"""
This module handles the JWT authentication model and essential API validations.
"""

# Core modules
import datetime

# 3rd party imports
import json
from flask import jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token, verify_jwt_in_request, get_jwt

# Application modules
from core import config
from core.lib.exceptions import *
from core.db import db_conn


class User(object):
    """
    Class representing a User.
    """

    def __init__(self, _id, username, role):
        self.id = _id
        self.username = username
        self.role = role

    def __str__(self):
        return "User(id='{id}', username='{username}', role='{role}')".format(id=self.id,
                                                                              username=self.username,
                                                                              role=self.role)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=None)

    @staticmethod
    def fromJSON(userjson):
        userdic = json.loads(userjson)
        return User(userdic["id"], userdic["username"], userdic["role"])


def generate_token(username, password):
    """
    Reads the username and password parameters in the query string and generates a JWT with it. The JWT includes an
    access token and a refresh token.

    :param username: The username to generate a token for
    :param password: The password associated with the username
    :returns: A Flask response which contains a JWT Token Payload to be used as Bearer
    :raises UserMessageException: Raised when the user credentials are invalid
    """

    # Find the user in the database
    dbuser = db_conn.query_user(username, password)

    # If User was found
    if dbuser is not None:
        # Create the User object
        user = User(dbuser.id(), dbuser.username(), dbuser.role())

        # Create a fresh token payload
        return _create_token_payload(user, True)

    else:
        # Couldn't find the User
        raise UserMessageException(401, "Invalid credentials.", "Crédits invalides.")


def refresh_token(ref_token):
    """
    Reads the refresh_token in the query string, validates it and creates another JWT with it. The JWT includes an
    access token and a refresh token.

    :param ref_token: The refresh token to verify
    :returns: A Flask response which contains a JWT Token Payload to be used as Bearer
    :raises UserMessageException: Raised when the refresh token is invalid
    """

    # Decodes the token. Will succeed only if valid.
    payload = decode_token(ref_token)

    # If refresh token only
    if payload["type"] == "refresh":
        # Create an unfresh token payload
        return _create_token_payload(User.fromJSON(payload["sub"]), False)

    else:
        # Invalid refresh token
        raise UserMessageException(400,
                                   "Only refresh tokens are allowed.",
                                   "Seuls les tokens de type refresh sont permis.")


def logout():
    """
    Logs out the current User completely and blacklists their token in the database.

    :returns: True if the token has been revoked.
    """

    # Get the jwt_token
    jwt_token = get_jwt()

    # Revoke the token for real in the blacklist
    return db_conn.add_token_revoked(jwt_token["jti"], datetime.datetime.fromtimestamp(jwt_token["exp"]))


def current_user():
    """
    Gets the User object from the token.

    :returns: If the token is valid a :class:`~auth.User` object representing the currently logged User is returned.
     Otherwise, None is returned.
    """

    try:
        # Verify jwt
        verify_jwt_in_request(optional=True)

        # Get the jwt_token
        jwt_token = get_jwt()

        # If valid
        if 'sub' in jwt_token:
            # Validate still good, role 1 is enough for this check
            validate_user(1)

            # Parse the token info to a User object
            return User.fromJSON(jwt_token["sub"])

    except (Exception,):
        # Token probably was existing and was invalid (for example, expired)
        return None
    return None


def check_token_revoked(jwt_data_jti):
    """
    Checks if the token has been revoked.

    :param jwt_data_jti: The jwt jti data from the token.
    :returns: True if the token has been revoked (if the user has logged out manually somewhere).
    """

    # Try to find the token in the revoked tokens in the database
    return db_conn.query_token_revoked(jwt_data_jti)


def validate_user(role_level):
    """
    Validates the current user and raises exceptions when validation fails.

    :param role_level: The role level the user should have
    :raises TokenInsufficientException: Raised when the token is missing privileges.
    :raises TokenRevokedException: Raised when the token has been revoked.
    :raises TokenInvalidException: Raised when the token is invalid.
    """

    # Verify the jwt
    verify_jwt_in_request()
    jwt_data = get_jwt()

    # If the grab worked and the sub identity key exists
    if 'sub' in jwt_data:
        # Read the User
        user = User.fromJSON(jwt_data["sub"])

        # Check if the token has not been revoked
        if 'jti' in jwt_data and not check_token_revoked(jwt_data['jti']):
            # If sufficient role (or just no role check at all)
            if role_level == 0 or user.role >= role_level:
                # Ok
                return True

            else:
                # Insufficient permission
                raise TokenInsufficientException()

        else:
            # Token revoked
            raise TokenRevokedException()

    else:
        # Unexpected crash
        raise TokenInvalidException()


def _create_token_payload(user, fresh):
    """
    Creates an official JWT Bearer response which contains 2 payload-tokens:
     (1) the official access token and
     (2) the refresh token.

    :returns: A JSON indicating a standard JWT Bearer response.
    """

    # The access token
    return jsonify(
        token_type="Bearer",
        expires_in=config.TOKEN_EXP_MINUTES * 60,
        refresh_expires_in=config.TOKEN_REFRESH_EXP_MINUTES * 60,
        access_token=create_access_token(user.toJSON(), fresh=fresh),
        refresh_token=create_refresh_token(user.toJSON())
    )
