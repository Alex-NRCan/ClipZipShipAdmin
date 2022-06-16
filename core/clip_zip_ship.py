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
    # Redirect
    records = db_conn.query_parents()

    # Group the records by theme
    theme_parents = {}
    for r in records:
        if not r["theme_uuid"] in theme_parents:
            # Create the theme/parents group
            theme_parents[r["theme_uuid"]] = {
                "theme_uuid": r["theme_uuid"],
                "theme_en": r["theme_title_en"],
                "theme_fr": r["theme_title_fr"],
                "parents": []
              }
        
        # Get the parents list
        parents_list = theme_parents[r["theme_uuid"]]["parents"]
        parents_list.append({
            "parent_uuid": r["parent_uuid"],
            "parent_en": r["parent_title_en"],
            "parent_fr": r["parent_title_fr"]
          })

    return [{
        "theme_uuid": k,
        "theme_en": v["theme_en"],
        "theme_fr": v["theme_fr"],
        "parents": v["parents"]
      } for k, v in theme_parents.items()]


def add_collection(data):
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
    if data["type"] == "feature":
        data_queryables = data["table_queryables"] or []
        data_queryables = [d.strip() for d in data_queryables]

        # Add feature collection
        return db_conn.add_collection_feature(data["parent_uuid"], data["metadata_uuid"], data["name"], data["title_en"], data["title_fr"], data["description_en"], data["description_fr"], data["keywords_en"], data["keywords_fr"], data["crs"],
                                              'feature', 'PostgreSQL', 
                                              data["extent_bbox"], data["extent_crs"], date_extent_temporal_begin, date_extent_temporal_end, data["geom_wkt"], data["geom_crs"],
                                              'text/html', 'canonical', 'Metadata Record - Open Canada Portal', 'https://open.canada.ca/data/en/dataset/' + data["metadata_uuid"], 'en-CA',
                                              data["table_name"], data["table_id_field"], data_queryables, config.DB_HOST, config.DB_NAME_FEATURES, config.DB_USER, config.DB_PASS, config.DB_SCHEMA_FEATURES)

    elif data["type"] == "coverage":
        # Guess the mime/type
        mimetype, encoding = mimetypes.guess_type(data["cov_data"])

        # Add coverage collection
        return db_conn.add_collection_coverage(data["parent_uuid"], data["metadata_uuid"], data["name"], data["title_en"], data["title_fr"], data["description_en"], data["description_fr"], data["keywords_en"], data["keywords_fr"], data["crs"],
                                               'coverage', 'rasterio', 
                                               data["extent_bbox"], data["extent_crs"], date_extent_temporal_begin, date_extent_temporal_end, data["geom_wkt"], data["geom_crs"],
                                               'text/html', 'canonical', 'Metadata Record - Open Canada Portal', 'https://open.canada.ca/data/en/dataset/' + data["metadata_uuid"], 'en-CA',
                                               data["cov_data"], data["cov_format_name"], mimetype)

    else:
        raise UserMessageException(500,
                                   "Collection provider type invalid.",
                                   "Type de fournisseur de collection invalide.")


def delete_collection(coll_name: str):
    # Redirect
    return db_conn.delete_collection(coll_name)


