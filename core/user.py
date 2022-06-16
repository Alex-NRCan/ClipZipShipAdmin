"""
This module handles Users management logic (create User, read User permissions, etc).
"""

# Imports
# 3rd party imports

# Application modules
from core.db import db_conn
from core.lib.exceptions import *


def get_users():
    """
    Gets a list of users in the system.
    """

    return db_conn.query_users()


def create_user(username, password):
    """
    Verifies if the user doesn't already exist and adds it in the database.

    :param username: The username of the User to create
    :param password: The password of the User to create
    :raises UserMessageException: Raised when the username already existed or no username was defined.
    """

    # Validate the username and password is set
    if username and password:
        # Trim it
        username = username.strip()

        # Get the user by name
        user = db_conn.query_user_by_username(username)

        # If no user by this username
        if user is None:
            # Add the User in the database
            db_conn.add_user(username, password)

        else:
            raise UserMessageException(500,
                                       "This username already exists.",
                                       "Ce nom d'utilisateur existe déjà.")

    else:
        raise UserMessageException(400,
                                   "Username or password undefined.",
                                   "Aucun nom d'utilisateur ou mot de passe défini.")


def update_user(username, patch_operations):
    """
    Updates the given user in the database.

    :param username: The username of the User to update
    :param patch_operations: The list of operations to apply on the user
    :raises UserMessageException: Raised when no username was defined.
    """
    # Validate the username and password is set
    if username and isinstance(patch_operations, list):
        # Get the user by name
        user = db_conn.query_user_by_username(username)

        # If no user by this username
        if user is not None:
            # For each operation
            for op in patch_operations:
                # If updating the username
                if 'path' in op and op['path'] == "/username":
                    db_conn.update_user(username, op['value'])

        else:
            raise UserMessageException(404,
                                       "Username couldn't be found.",
                                       "Ce nom d'utilisateur n'existe pas.")

    else:
        raise UserMessageException(400,
                                   "Username undefined or invalid PATCH operations series.",
                                   "Aucun nom d'utilisateur défini ou série d'opérations PATCH invalide.")


def delete_user(username):
    """
    Verifies if the user exists and deletes it from the database.

    :param username: The username of the User to delete
    :raises UserMessageException: Raised when the username doesn't exist or no username was defined.
    """

    # Validate the username is set
    if username:
        # Trim it
        username = username.strip()

        # Get the user by name
        user = db_conn.query_user_by_username(username)

        # If user exists
        if user is not None:
            # Delete the user in the database
            db_conn.delete_user(user.id())

        else:
            raise UserMessageException(404,
                                       "Username couldn't be found.",
                                       "Ce nom d'utilisateur n'existe pas.")

    else:
        raise UserMessageException(400,
                                   "Username undefined.",
                                   "Aucun nom d'utilisateur défini.")
