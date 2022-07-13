"""
This module handles the NRCan business logic to work with the Quality metadata information.
"""

# Imports
# 3rd party imports
from flask import json
import requests, xmltodict, psycopg2
from dateutil import parser as date_parser
import mimetypes

# Application modules
from core import config
from core.lib.exceptions import *
from core.db import db_conn


def get_parents():
  """
  Gets the parents.

  :returns: The list of parents and themes.
  """
  
  # Redirect
  records = db_conn.query_parents()

  # Group the records by theme
  theme_parents = {}
  for r in records:
      if not r["theme_uuid"] in theme_parents:
          # Create the theme/parents group
          theme_parents[r["theme_uuid"]] = {
              "theme_uuid": r["theme_uuid"],
              "title": {
                "en": r["theme_title_en"],
                "fr": r["theme_title_fr"]
              },
              "parents": []
            }
      
      # Get the parents list
      parents_list = theme_parents[r["theme_uuid"]]["parents"]
      parents_list.append({
          "parent_uuid": r["parent_uuid"],
          "title": {
            "en": r["parent_title_en"],
            "fr": r["parent_title_fr"]
          }
        })

  return [{
      "theme_uuid": k,
      "title": {
        "en": v["title"]["en"],
        "fr": v["title"]["fr"]
      },
      "parents": v["parents"]
    } for k, v in theme_parents.items()]


def get_extent(schema: str, table_name: str, out_crs: int, data: dict):
  """
  Gets the extent of the specified table in the specified spatial reference.

  :param schema: The schema name of the table to retrieve the extent of.
  :param table_name: The table name of the table to retrieve the extent of.
  :param out_crs: The spatial reference that we want the extent into.
  :param data: The dictionary containing the information to connect to the remote database.
  :returns: The extent of the given spatial table.
  """

  try:
    # If no db_host
    if "db_host" not in data or not data["db_host"] or data["db_host"] == "":
        raise UserMessageException(500,
                                   "Database host not specified.",
                                   "Hôte de la base de données non spécifié.")
    
    # If no db_port
    if "db_port" not in data or not data["db_port"] or data["db_port"] == "":
        raise UserMessageException(500,
                                   "Database port not specified.",
                                   "Port de la base de données non spécifié.")

    # If no db_name
    if "db_name" not in data or not data["db_name"] or data["db_name"] == "":
        raise UserMessageException(500,
                                   "Database name not specified.",
                                   "Nom de la base de données non spécifié.")

    # If no db_user
    if "db_user" not in data or not data["db_user"] or data["db_user"] == "":
        raise UserMessageException(500,
                                   "Database username not specified.",
                                   "Utilisateur de la base de données non spécifié.")

    # If no db_password
    if "db_password" not in data or not data["db_password"] or data["db_password"] == "":
        raise UserMessageException(500,
                                   "Database password not specified.",
                                   "Mot de passe de la base de données non spécifié.")
    
    # Redirect
    return db_conn.get_table_extent(schema, table_name, out_crs, data["db_host"], data["db_port"], data["db_name"], data["db_user"], data["db_password"])

  except UserMessageException as err:
    raise err

  except Exception:
    # Raise the error
    raise UserMessageException(500,
                               "Couldn't find extent for the given table: " + table_name,
                               "Impossible de déterminer l'étendu spatial de la table: " + table_name)


def add_parent(data):
  """
  Adds a parent in the system.

  :param data: The Python dictionary representing the information on the parent to be added.
               
                     Properties in data are:
                      - theme_uuid: The theme identifier under which to add the parent.
                      - title_en: The English title of the parent to be added.
                      - title_fr: The French title of the parent to be added.

  :returns: True when added
  """

  try:
    # Redirect
    return db_conn.add_parent(data["theme_uuid"], data["title_en"], data["title_fr"])

  except psycopg2.DatabaseError as err:
    if err.pgcode == config.DB_PG_CODE:
      raise UserMessageException(500,
                                 "Error adding the parent: " + err.diag.message_primary,
                                 "Erreur lors de l'ajout du parent: " + err.diag.message_primary) from err
    else:
      raise


def delete_parent(parent_uuid: str):
  """
  Deletes a parent if there are no collections attached to it.

  :param parent_uuid: The parent identifier to delete.

  :returns: True when deleted
  """

  try:
    # Redirect
    return db_conn.delete_parent(parent_uuid)

  except psycopg2.DatabaseError as err:
    if err.pgcode == config.DB_PG_CODE:
      raise UserMessageException(500,
                                 "Error deleting the parent: " + err.diag.message_primary,
                                 "Erreur lors de la suppression du parent: " + err.diag.message_primary) from err
    else:
      raise


def add_collection(data):
  """
  Adds a collection in the system.

  :param data: The Python dictionary holding all information on the collection to add.
               
               For all types, properties are:
                - type: can be 1 of 2 values: "feature" or "coverage"
                - parent_uuid: indicates the parent identifier on which to add the collection
                - metadata_uuid: indicates the metadata catalog identifier representing the collection
                - name: the collection name (must be unique)
                - title_en: the English title of the collection
                - title_fr: the French title of the collection
                - description_en: the English description of the collection
                - description_fr: the French description of the collection
                - keywords_en: the English keywords of the collection
                - keywords_fr: the French keywords of the collection
                - crs: the spatial reference of the collection
                - extent_bbox: the spatial extent of the bbox representing the collection
                - extent_crs: the spatial reference of the extent bbox
                - extent_temporal_begin: the starting date for the data in the collection
                - extent_temporal_end: the ending date for the data in the collection
                
                For type=="feature":
                - table_name: the table name of the feature type collection being added
                - table_schema: the database schema holding the table
                - db_host: the host of the database
                - db_port: the connection port of the database
                - db_name: the database name
                - db_user: the username to connect to the database
                - db_password: the password for the user
                - table_id_field: the field in the table which holds the identifier key
                - table_queryables: the list of queryables fields in the table

                For type=="coverage":
                - geom_wkt: the geometry in well known text format
                - geom_crs: the spatial reference for the geometry wkt
                - cov_data: the cog of the raster
                - cov_format_name: the format name of the cog file (e.g.: GTiff)

  :returns: True when added
  """

  # If an extent_temporal_begin is specified
  date_extent_temporal_begin = None
  if data["extent_temporal_begin"]:
    try:
        date_extent_temporal_begin = str(date_parser.parse(data["extent_temporal_begin"]))
    
    except Exception as err:
        # Raise the error
        raise UserMessageException(500,
                                   "Invalid temporal extent begin.",
                                   "Étendu temporel de début invalide.")

  # If an extent_temporal_end is specified
  date_extent_temporal_end = None
  if data["extent_temporal_end"]:
    try:
        date_extent_temporal_end = str(date_parser.parse(data["extent_temporal_end"]))

    except Exception as err:
        # Raise the error
        raise UserMessageException(500,
                                   "Invalid temporal extent end.",
                                   "Étendu temporel de fin invalide.")

  # Depending on the collection type
  result = None
  try:
    if data["type"] == "feature":
        # Massage the inputs
        data_queryables = data["table_queryables"] or []
        data_queryables = [d.strip() for d in data_queryables]
        data_queryables = list(filter(lambda d: len(d) > 0, data_queryables))

        # Add feature collection
        result = db_conn.add_collection_feature(data["parent_uuid"], data["metadata_uuid"], data["name"], data["title_en"], data["title_fr"], data["description_en"], data["description_fr"], data["keywords_en"], data["keywords_fr"], data["crs"],
                                               'feature', 'PostgreSQL', 
                                               data["extent_bbox"], data["extent_crs"], date_extent_temporal_begin, date_extent_temporal_end,
                                               'text/html', 'canonical', 'Metadata Record - Open Canada Portal', 'https://open.canada.ca/data/en/dataset/' + data["metadata_uuid"], 'en-CA',
                                               data["table_name"], data["table_id_field"], data_queryables, data["db_host"], data["db_port"], data["db_name"], data["db_user"], data["db_password"], [data["table_schema"]])

    elif data["type"] == "coverage":
        # Guess the mime/type
        mimetype, encoding = mimetypes.guess_type(data["cov_data"])

        # Add coverage collection
        result = db_conn.add_collection_coverage(data["parent_uuid"], data["metadata_uuid"], data["name"], data["title_en"], data["title_fr"], data["description_en"], data["description_fr"], data["keywords_en"], data["keywords_fr"], data["crs"],
                                                'coverage', 'rasterio', 
                                                data["extent_bbox"], data["extent_crs"], date_extent_temporal_begin, date_extent_temporal_end, data["geom_wkt"], data["geom_crs"],
                                                'text/html', 'canonical', 'Metadata Record - Open Canada Portal', 'https://open.canada.ca/data/en/dataset/' + data["metadata_uuid"], 'en-CA',
                                                data["cov_data"], data["cov_format_name"], mimetype)

    else:
        raise UserMessageException(500,
                                   "Collection provider type invalid.",
                                   "Type de fournisseur de collection invalide.")

    # The collection has been added. Tell PyGeoAPI to hot-reload
    response = requests.get(config.PYGEOAPI_URL)

    # Return the result of the adding of the collection
    return result

  except psycopg2.DatabaseError as err:
    if err.pgcode == config.DB_PG_CODE:
        raise UserMessageException(500,
                                   "Error adding the collection: " + err.diag.message_primary,
                                   "Erreur lors de l'ajout de la collection: " + err.diag.message_primary) from err
    else:
        raise


def update_collection(coll_name: str, body_patch):
  """
  Updates a collection.

  :param coll_name: The collection name to update.
  :param body_patch: The Python dictionary representing the information to update.
               
                     Properties in body_patch are:
                      - geometry: True when the geometry must be updated

  :returns: True when updated
  """

  # If updating the geometry
  if "geometry" in body_patch and body_patch["geometry"]:
    # Update the geometry
    return db_conn.update_collection_geom(coll_name)
  return True


def delete_collection(coll_name: str):
  """
  Deletes a collection.
  
  :param coll_name: The collection name to delete.

  :returns: True when deleted
  """

  # Redirect
  return db_conn.delete_collection(coll_name)


