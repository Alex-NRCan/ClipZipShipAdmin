"""
This module, implementing OpenAPI concepts, manages the various routes for the API.

End points:
 - /api/login (login) enables JWT authentication using username/password
 - /api/refresh (refresh) enables JWT re-authentication using a refresh token
 - /api/logout (logout) logs out the current User
 - /api/collections Adds (PUT) a Collection
 - /api/collections/{collection} Deletes (DELETE) a Collection
 - /api/user Creates (POST) a User in the database
 - /api/user/{user} Updates (PATCH) or Deletes (DELETE) a User in the database
 - /api/metadata/<uuid> Gets metadata information from the FGP CSW Catalog in a Json format
 - /api/parents Gets the available Parents, grouped by Themes, for the Collections
"""

# 3rd party imports
import requests, json
from flask import request, current_app, jsonify
from uuid import UUID

# Application imports
from core import config, user, auth, clip_zip_ship
from core.geonetwork import GeoNetworkReader
from core.lib.exceptions import *
from core.routes import rt_core
from . import routes


@routes.route('/api/login', methods=["POST"])
def login():
    """
    Handles a POST request on "/api/login" end point to authenticate a User with a username and password.
    """

    try:
        # Validate the parameters
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


@routes.route('/api/refresh', methods=["POST"])
def refresh():
    """
    Handles a POST request on "/api/refresh" end point to return a new User token.
    """

    try:
        # Validate the parameters
        body = request.json
        if "refresh_token" in body:
            # Redirect
            return auth.refresh_token(body["refresh_token"])

        else:
            # Parameters invalid
            raise ParametersInvalidException()

    except UserMessageException as err:
        # Handle the error for the User
        rt_core.abort_user_message(err)

    except Exception as err:
        # Raise a generic error
        rt_core.abort_error(err)


@routes.route('/api/logout', methods=["DELETE"])
@rt_core.validate_user_level(config.ROLE_LEVEL_USER)
def logout():
    """
    Handles a DELETE request on "/api/logout" end point to logout a User.
    """

    try:
        # Redirect
        if auth.logout():
            return rt_core.response_204()

        else:
            raise UserMessageException(500, "Failed to logout from the API completely",
                                       "La tentative de déconnexion de l'API ne s'est pas bien terminée")

    except UserMessageException as err:
        # Handle the error for the User
        rt_core.abort_user_message(err)

    except Exception as err:
        # Raise a generic error
        rt_core.abort_error(err)


@routes.route('/api/collections', methods=["PUT"])
@rt_core.validate_user_level(config.ROLE_LEVEL_ADMIN)
def put_collections():
    """
    Handles a PUT request on end point "/api/collections" to add a Collection.
    """

    try:
        d = request.data
        
        if d:
            d = d.decode()
            d = json.loads(d)

        # Redirect
        clip_zip_ship.add_collection(d)

        # Respond
        return rt_core.response_201("")

    except UserMessageException as err:
        # Handle the error for the User
        rt_core.abort_user_message(err)

    except Exception as err:
        # Raise a generic error
        rt_core.abort_error(err)


@routes.route('/api/collections/<collection>', methods=["DELETE"])
@rt_core.validate_user_level(config.ROLE_LEVEL_ADMIN)
def delete_collection(collection):
    """
    Handles a DELETE request on end point "/api/collections" to return the Collection information.
    """

    try:
        # Redirect
        deleted = clip_zip_ship.delete_collection(collection)

        # Respond
        if deleted:
            return rt_core.response_204()
        
        else:
            return rt_core.redirect_not_found()

    except UserMessageException as err:
        # Handle the error for the User
        rt_core.abort_user_message(err)

    except Exception as err:
        # Raise a generic error
        rt_core.abort_error(err)


@routes.route('/api/collections/<collection>', methods=["PATCH"])
@rt_core.validate_user_level(config.ROLE_LEVEL_ADMIN)
def patch_collection(collection):
    """
    Handles a PATCH request on end point "/api/users" to update a user of the system.
    """

    try:
        # Get the users
        body = request.json
        clip_zip_ship.update_collection(collection, body)

        # Return 204
        return rt_core.response_204()

    except UserMessageException as err:
        # Handle the error for the User
        rt_core.abort_user_message(err)

    except Exception as err:
        # Raise a generic error
        rt_core.abort_error(err)


@routes.route('/api/metadata/<uuid>', methods=["GET"])
@rt_core.validate_user_level(config.ROLE_LEVEL_ADMIN)
def get_metadata(uuid):
    """
    Handles a GET request on end point "/api/metadata/{uuid}" to return the Metadata information.
    """

    try:
        # Validate the uuid is valid uuid
        if not is_valid_uuid(uuid):
            raise UserMessageException(500,
                                       "Invalide UUID.",
                                       "UUID invalid.")

        # Connect to GeoNetwork to get the XML
        response = requests.get(config.CATALOG_URL.format(metadata_uuid=uuid))

        # Create class
        geonetwork = GeoNetworkReader(response.text)
        
        # Return the dictionary
        return geonetwork.to_dict()

    except UserMessageException as err:
        # Handle the error for the User
        rt_core.abort_user_message(err)

    except Exception as err:
        # Raise a generic error
        rt_core.abort_error(err)


@routes.route('/api/parents', methods=["GET"])
@rt_core.validate_user_level(config.ROLE_LEVEL_ADMIN)
def get_parents():
    """
    Handles a GET request on end point "/api/parents" to return the Parents information.
    """

    try:
        # Redirect
        return clip_zip_ship.get_parents()

    except UserMessageException as err:
        # Handle the error for the User
        rt_core.abort_user_message(err)

    except Exception as err:
        # Raise a generic error
        rt_core.abort_error(err)


@routes.route('/api/parents', methods=["PUT"])
@rt_core.validate_user_level(config.ROLE_LEVEL_ADMIN)
def put_parent():
    """
    Handles a PUT request on end point "/api/parents" to add a parent for Collections.
    """

    try:
        d = request.data
        
        if d:
            d = d.decode()
            d = json.loads(d)

        # Redirect
        parent_uuid = clip_zip_ship.add_parent(d)

        # Respond
        return rt_core.response_201(parent_uuid)

    except UserMessageException as err:
        # Handle the error for the User
        rt_core.abort_user_message(err)

    except Exception as err:
        # Raise a generic error
        rt_core.abort_error(err)


@routes.route('/api/parents/<uuid>', methods=["DELETE"])
@rt_core.validate_user_level(config.ROLE_LEVEL_ADMIN)
def delete_parent(uuid):
    """
    Handles a DELETE request on end point "/api/parents/"<uuid> to delete a Parent.
    """

    try:
        # Redirect
        deleted = clip_zip_ship.delete_parent(uuid)

        # Respond
        if deleted:
            return rt_core.response_204()
        
        else:
            return rt_core.redirect_not_found()

    except UserMessageException as err:
        # Handle the error for the User
        rt_core.abort_user_message(err)

    except Exception as err:
        # Raise a generic error
        rt_core.abort_error(err)


@routes.route('/api/extent/<schema>/<table_name>/<out_crs>', methods=["GET"], defaults={'schema': 'nrcan', 'table_name': None, 'out_crs': 4326})
@rt_core.validate_user_level(config.ROLE_LEVEL_ADMIN)
def get_extent(schema: str, table_name: str, out_crs: int):
    """
    Handles a GET request on end point "/api/extent/<table_name>" to return the Parents information.
    """

    try:
        # Read the data
        d = request.data
        
        if d:
            d = d.decode()
            d = json.loads(d)

        # Redirect
        return clip_zip_ship.get_extent(schema, table_name, out_crs, d)

    except UserMessageException as err:
        # Handle the error for the User
        rt_core.abort_user_message(err)

    except Exception as err:
        # Raise a generic error
        rt_core.abort_error(err)


@routes.route('/api/users', methods=["GET"])
@rt_core.validate_user_level(config.ROLE_LEVEL_ADMIN)
def get_users():
    """
    Handles a GET request on end point "/api/users" to get all Users of the system.
    """

    try:
        # Get the users
        users = user.get_users()

        # Parse and return
        return [x.to_json_simple() for x in users]

    except UserMessageException as err:
        # Handle the error for the User
        rt_core.abort_user_message(err)

    except Exception as err:
        # Raise a generic error
        rt_core.abort_error(err)


@routes.route('/api/user', methods=["POST"])
@rt_core.validate_user_level(config.ROLE_LEVEL_ADMIN)
def post_user():
    """
    Handles a POST request on end point "/api/user" to create a User.
    """

    try:
        # Validate the parameters
        body = request.json
        if "username" in body and "password" in body:
            # Create the User
            user.create_user(body["username"], body["password"])
            return rt_core.response_201("")

        else:
            # Parameters invalid
            raise ParametersInvalidException()

    except UserMessageException as err:
        # Handle the error for the User
        rt_core.abort_user_message(err)

    except Exception as err:
        # Raise a generic error
        rt_core.abort_error(err)


@routes.route('/api/users/<username>', methods=["PATCH"])
@rt_core.validate_user_level(config.ROLE_LEVEL_ADMIN)
def patch_users(username):
    """
    Handles a PATCH request on end point "/api/users" to update a user of the system.
    """

    try:
        # Get the users
        body = request.json
        user.update_user(username, body)

        # Return 204
        return rt_core.response_204()

    except UserMessageException as err:
        # Handle the error for the User
        rt_core.abort_user_message(err)

    except Exception as err:
        # Raise a generic error
        rt_core.abort_error(err)


@routes.route('/api/user/<username>', methods=["DELETE"])
@rt_core.validate_user_level(config.ROLE_LEVEL_ADMIN)
def delete_user(username):
    """
    Handles a DELETE request on end point "/api/user" to delete a User.
    """

    try:
        # Delete the User
        user.delete_user(username)
        return rt_core.response_204()

    except UserMessageException as err:
        # Handle the error for the User
        rt_core.abort_user_message(err)

    except Exception as err:
        # Raise a generic error
        rt_core.abort_error(err)





def is_valid_uuid(uuid_to_test, version=4):
    """
    Check if uuid_to_test is a valid UUID.
    
     Parameters
    ----------
    uuid_to_test : str
    version : {1, 2, 3, 4}
    
     Returns
    -------
    `True` if uuid_to_test is a valid UUID, otherwise `False`.
    
     Examples
    --------
    >>> is_valid_uuid('c9bf9e57-1685-4c89-bafb-ff5af830be8a')
    True
    >>> is_valid_uuid('c9bf9e58')
    False
    """
    
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test
