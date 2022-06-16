"""
This package offers database connection.
"""

# 3rd party imports
from core import config
from . import db_connection

# Create the database connection object which is GLOBAL
db_conn = db_connection.DBConnection(host=config.DB_HOST, dbname=config.DB_NAME,
                                     user=config.DB_USER, password=config.DB_PASS)
