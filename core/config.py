"""
This module stores all configurations used by this application.
"""

import sys, getopt


# Environment variables
ENV = "DEV"  # Will be overriden from launch parameter
API_URL_DEV = "http://localhost:5001/api"
API_URL_PROD = "http://localhost:5001/api"

# Database variables
DB_HOST = {{DB_HOST}}
DB_NAME = {{DB_NAME}}
DB_NAME_FEATURES = {{DB_NAME_FEATURES}}
DB_USER = {{DB_USER}}
DB_PASS = {{DB_PASS}}
DB_SCHEMA = {{DB_SCHEMA}}
DB_SCHEMA_FEATURES = ["public"]

# Catalog URL
CATALOG_URL = "https://maps.canada.ca/geonetwork/srv/eng/csw?request=GetRecordById&service=CSW&version=2.0.2&elementSetName=full&outputSchema=http://www.isotc211.org/2005/gmd&typeNames=gmd:MD_Metadata&constraintLanguage=FILTER&id={metadata_uuid}"

# Determine if using Connexion API.
# Connexion is essentially useful for the Swagger UI and define the spec first.
USING_CONNEXION_API = True

# Security token variables
TOKEN_COOKIE_NAME = "web_token"
TOKEN_KEY_WEB = {{TOKEN_KEY_WEB}}
TOKEN_KEY_API = {{TOKEN_KEY_WEB}}
TOKEN_EXP_MINUTES = 480
TOKEN_REFRESH_EXP_MINUTES = 1440

# Roles
ROLE_LEVEL_ADMIN = 100
ROLE_LEVEL_USER = 1
ROLES = {
    "ADMIN": ROLE_LEVEL_ADMIN,
    "USER": ROLE_LEVEL_USER
}

DB_STORED_PROCS = {
    "ADD_COLLECTION_COVERAGE": "czs.czs_add_collection_coverage",
    "ADD_COLLECTION_FEATURE": "czs.czs_add_collection_feature",
    "DELETE_COLLECTION": "czs.czs_delete_collection"
}

DB_TABLE_COLLECTION_PARENT = {
    "TABLE_NAME": {{TABLE_NAME}},
    "FIELD_PARENT_UUID": "parent_uuid",
    "FIELD_TITLE_EN": "title_en",
    "FIELD_TITLE_FR": "title_fr",
}

DB_TABLE_COLLECTION_THEME = {
    "TABLE_NAME": {{TABLE_NAME}},
    "FIELD_THEME_UUID": "theme_uuid",
    "FIELD_TITLE_EN": "title_en",
    "FIELD_TITLE_FR": "title_fr",
}

DB_TABLE_USERS = {
    "TABLE_NAME": {{TABLE_NAME}},
    "FIELD_ID": "id",
    "FIELD_USERNAME": "username",
    "FIELD_PASSWORD": "password",
    "FIELD_ROLE": "role"
}

DB_TABLE_TOKEN_BLACKLIST = {
    "TABLE_NAME": {{TABLE_NAME}},
    "FIELD_ID": "id",
    "FIELD_JTI_UID": "jti_uid",
    "FIELD_EXP_DATE": "exp_date"
}

def read_param(param_name):
    opts, args = getopt.getopt(sys.argv[1:], "ae:p:", ["api=", "env=", "port="])
    for opt, arg in opts:
        if opt in ("-" + param_name, "--" + param_name):
            return arg
    return None

def IS_DEV():
    """
    Utility function to quickly check if application is running in the DEV environment.
    """
    return ENV == "DEV"

def API_URL():
    if IS_DEV():
        return API_URL_DEV
    else:
        return API_URL_PROD
