"""
This module offers functions to query and manage a Postgresql database.
"""

# 3rd party imports
import datetime

import psycopg2
import psycopg2.extras
from psycopg2 import sql

# Application modules
from core import config
from core.lib import encr
from .entity.user import DBUser


class DBConnection(object):
    """
    Class representing a Database connection.
    """

    def __init__(self, host, dbname, user, password):
        """
        Constructor
        """
        self.host = host
        self.dbname = dbname
        self.user = user
        self.password = password


    def open_conn(self):
        """
        Connects to the database.

        :returns: A :class:`~psycopg2` connection
        """

        # Connects and returns the connection
        return psycopg2.connect(host=self.host, dbname=self.dbname, user=self.user, password=self.password)


    def query_users(self):
        """
        Queries for all the Users in the system.

        :returns: A list of :class:`~entity.DBUser` objects
        """

        # Connect to the database
        with self.open_conn() as conn:
            # Open a cursor
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                str_query = "SELECT * FROM {table} ORDER BY {field_order}"

                # Query in the database
                query = sql.SQL(str_query).format(
                    table=sql.Identifier(config.DB_SCHEMA, config.DB_TABLE_USERS["TABLE_NAME"]),
                    field_order=sql.Identifier(config.DB_TABLE_USERS["FIELD_USERNAME"]))

                # Execute cursor and fetch
                cur.execute(query)
                res = cur.fetchall()
                users = []
                for u in res:
                    users.append(DBUser(u))
                return users


    def query_user_by_username(self, username):
        """
        Queries for a User in the database with only the username.

        :param username: The username of the User to query
        :returns: A :class:`~entity.DBUser` object when found a user; otherwise returns None
        """

        # Connect to the database
        with self.open_conn() as conn:
            # Open a cursor
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                str_query = "SELECT * FROM {table} WHERE UPPER({field_user}) = %s"

                # Query in the database
                query = sql.SQL(str_query).format(
                    table=sql.Identifier(config.DB_SCHEMA, config.DB_TABLE_USERS["TABLE_NAME"]),
                    field_user=sql.Identifier(config.DB_TABLE_USERS["FIELD_USERNAME"]))

                # Execute cursor and fetch
                cur.execute(query, (username.upper(),))
                u = cur.fetchone()
                if u:
                    return DBUser(u)
                else:
                    return None


    def query_user(self, username, password):
        """
        Queries for a User in the database with the username and password combination.

        :param username: The username of the User to query
        :param password: The password of the User to query.
        :returns: A :class:`~entity.DBUser` object when found a user; otherwise returns None
        """

        # Redirect
        user = self.query_user_by_username(username)

        # If a User was found
        if user:
            # Read password as bytes
            passbytes = bytes(user.password())

            # If the password is valid
            if encr.check_password(password, passbytes):
                # Valid user
                return user

        # None
        return None


    def add_user(self, username, password):
        """
        Adds a user in the database.

        :param username: The username of the User to create
        :param password: The password of the User to create. The password will be encrypted.
        """

        # Connect to the database
        with self.open_conn() as conn:
            # Open a cursor
            with conn.cursor() as cur:
                str_query = "INSERT INTO {table} ({field_user}, {field_password}) VALUES (%s, %s)"

                # Query in the database
                query = sql.SQL(str_query).format(
                    table=sql.Identifier(config.DB_SCHEMA, config.DB_TABLE_USERS["TABLE_NAME"]),
                    field_user=sql.Identifier(config.DB_TABLE_USERS["FIELD_USERNAME"]),
                    field_password=sql.Identifier(config.DB_TABLE_USERS["FIELD_PASSWORD"]))

                # Encrypt the password
                passencr = encr.get_hashed_password(password)

                # Execute cursor
                cur.execute(query, (username, passencr,))
            conn.commit()


    def update_user(self, username, new_username):
        """
        Updates a user in the database.

        :param username: The username of the User to update
        :param new_username: The new username.
        """

        # Connect to the database
        with self.open_conn() as conn:
            # Open a cursor
            with conn.cursor() as cur:
                str_query = "UPDATE {table} SET {field_user} = %s WHERE {field_user} = %s"

                # Query in the database
                query = sql.SQL(str_query).format(
                    table=sql.Identifier(config.DB_SCHEMA, config.DB_TABLE_USERS["TABLE_NAME"]),
                    field_user=sql.Identifier(config.DB_TABLE_USERS["FIELD_USERNAME"]))

                # Execute cursor
                cur.execute(query, (new_username, username,))
            conn.commit()


    def delete_user(self, user_id):
        """
        Deletes a user from the database.

        :param user_id: The User ID to delete
        """

        # Connect to the database
        with self.open_conn() as conn:
            # Open a cursor
            with conn.cursor() as cur:
                str_query = "DELETE FROM {table} WHERE {field}=%s;"

                # Query in the database
                query = sql.SQL(str_query).format(
                    table=sql.Identifier(config.DB_SCHEMA, config.DB_TABLE_USERS["TABLE_NAME"]),
                    field=sql.Identifier(config.DB_TABLE_USERS["FIELD_ID"]))

                # Execute cursor
                cur.execute(query, (user_id,))
            conn.commit()


    def query_token_revoked(self, jti_uid):
        """
        Queries the tokens blacklist table to see if the given token was revoked.

        :param jti_uid: The JTI of the Token to check if it has been revoked
        """

        # Connect to the database
        with self.open_conn() as conn:
            # Open a cursor
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                str_query = "SELECT * FROM {table} WHERE {field} = %s"

                # Query in the database
                query = sql.SQL(str_query).format(
                    table=sql.Identifier(config.DB_SCHEMA, config.DB_TABLE_TOKEN_BLACKLIST["TABLE_NAME"]),
                    field=sql.Identifier(config.DB_TABLE_TOKEN_BLACKLIST["FIELD_JTI_UID"]))

                # Execute cursor and fetch
                cur.execute(query, (jti_uid,))
                res = cur.fetchone()
                if res:
                    return res

        # None
        return None


    def add_token_revoked(self, jti_uid, expiration_date):
        """
        Adds a token in the tokens blacklist table so that the token becomes officially revoked.

        :param jti_uid: The JTI of the Token to add to the table in order to revoke it.
        :param expiration_date: The Expiration date of the Token being revoked. This serves to keep the
         table clean and not store revoked tokens forever in the database.
        """

        # Connect to the database
        with self.open_conn() as conn:
            # *For a lack of a better place to do this*
            # Clear the old revoked tokens to clean up the database with time
            # Open a cursor
            with conn.cursor() as cur:
                str_query = "DELETE FROM {table} WHERE {field} < %s;"

                # Query in the database
                query = sql.SQL(str_query).format(
                    table=sql.Identifier(config.DB_SCHEMA, config.DB_TABLE_TOKEN_BLACKLIST["TABLE_NAME"]),
                    field=sql.Identifier(config.DB_TABLE_TOKEN_BLACKLIST["FIELD_EXP_DATE"]))

                # Execute cursor
                cur.execute(query, (datetime.datetime.now(),))

            # Open a cursor
            with conn.cursor() as cur:
                str_query = "INSERT INTO {table} ({field_jti_uid}, {field_exp_date}) VALUES (%s, %s)"

                # Query in the database
                query = sql.SQL(str_query).format(
                    table=sql.Identifier(config.DB_SCHEMA, config.DB_TABLE_TOKEN_BLACKLIST["TABLE_NAME"]),
                    field_jti_uid=sql.Identifier(config.DB_TABLE_TOKEN_BLACKLIST["FIELD_JTI_UID"]),
                    field_exp_date=sql.Identifier(config.DB_TABLE_TOKEN_BLACKLIST["FIELD_EXP_DATE"]))

                # Execute cursor
                cur.execute(query, (jti_uid, expiration_date,))
            conn.commit()
            return True


    def query_parents(self):
        """
        Queries for all the Parents/Themes in the system.

        :returns: A list of parents linked with their themes.
        """

        # Connect to the database
        with self.open_conn() as conn:
            # Open a cursor
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                str_query = """SELECT p.{field_parent_uuid},
                                      t.{field_theme_uuid},
                                      p.{field_parent_title_en} AS parent_title_en,
                                      p.{field_parent_title_fr} AS parent_title_fr,
                                      t.{field_theme_title_en} AS theme_title_en,
                                      t.{field_theme_title_fr} AS theme_title_fr
                               FROM {table_parent} p JOIN {table_theme} t ON p.{field_theme_uuid}=t.{field_theme_uuid} ORDER BY p.{field_parent_title_en}"""

                # Query in the database
                query = sql.SQL(str_query).format(
                    field_parent_uuid=sql.Identifier(config.DB_TABLE_COLLECTION_PARENT["FIELD_PARENT_UUID"]),
                    field_theme_uuid=sql.Identifier(config.DB_TABLE_COLLECTION_THEME["FIELD_THEME_UUID"]),
                    field_parent_title_en=sql.Identifier(config.DB_TABLE_COLLECTION_PARENT["FIELD_TITLE_EN"]),
                    field_parent_title_fr=sql.Identifier(config.DB_TABLE_COLLECTION_PARENT["FIELD_TITLE_FR"]),
                    field_theme_title_en=sql.Identifier(config.DB_TABLE_COLLECTION_THEME["FIELD_TITLE_EN"]),
                    field_theme_title_fr=sql.Identifier(config.DB_TABLE_COLLECTION_THEME["FIELD_TITLE_FR"]),
                    table_parent=sql.Identifier(config.DB_SCHEMA, config.DB_TABLE_COLLECTION_PARENT["TABLE_NAME"]),
                    table_theme=sql.Identifier(config.DB_SCHEMA, config.DB_TABLE_COLLECTION_THEME["TABLE_NAME"]))

                # Execute cursor and fetch
                cur.execute(query)
                return cur.fetchall()


    def add_collection_feature(self, parent_uuid: str, metadata_uuid: str, coll_name: str, coll_title_en: str, coll_title_fr: str, coll_desc_en: str, coll_desc_fr: str,
                               keywords_en: list, keywords_fr: list, coll_crs: int, provider_type: str, provider_name: str,
                               extent_bbox: list, extent_crs: str, extent_temporal_begin: object, extent_temporal_end: object, geom_wkt: str, geom_crs: int,
                               link_type: str, link_rel: str, link_title: str, link_href: str, link_hreflang: str,
                               tablename: str, data_id_field: str, data_queryables: str, db_host: str, db_name: str, db_user: str, db_password: str, db_search_path: list):
        """
        Adds a feature collection to the database.
        """

        # Connect to the database
        with self.open_conn() as conn:
            # Open a cursor
            with conn.cursor() as cur:
                # Call the stored procedure
                cur.execute("CALL " + config.DB_STORED_PROCS["ADD_COLLECTION_FEATURE"] + "(%s, %s, %s, %s, %s, %s, \
                              %s, %s, %s, %s, %s, \
                              %s, %s, %s, %s, %s, %s, %s, \
                              %s, %s, %s, %s, %s, \
                              %s, %s, %s, %s, %s, %s, %s, %s);",
                              (
                                parent_uuid, metadata_uuid, coll_name, coll_title_en, coll_title_fr, coll_desc_en,
                                coll_desc_fr, keywords_en, keywords_fr, coll_crs, provider_type,
                                provider_name, extent_bbox, extent_crs, extent_temporal_begin, extent_temporal_end, geom_wkt, geom_crs,
                                link_type, link_rel, link_title, link_href, link_hreflang,
                                tablename, data_id_field, data_queryables, db_host, db_name, db_user, db_password, db_search_path,
                              )
                            )

            conn.commit()
            return True


    def add_collection_coverage(self, parent_uuid: str, metadata_uuid: str, coll_name: str, coll_title_en: str, coll_title_fr: str, coll_desc_en: str, coll_desc_fr: str,
                               keywords_en: list, keywords_fr: list, coll_crs: int, provider_type: str, provider_name: str,
                               extent_bbox: list, extent_crs: str, extent_temporal_begin: object, extent_temporal_end: object, geom_wkt: str, geom_crs: int,
                               link_type: str, link_rel: str, link_title: str, link_href: str, link_hreflang: str,
                               cov_data: str, format_name: str, format_mimetype: str):
        """
        Adds a coverage collection to the database.
        """

        # Connect to the database
        with self.open_conn() as conn:
            # Open a cursor
            with conn.cursor() as cur:
                # Call the stored procedure
                cur.execute("CALL " + config.DB_STORED_PROCS["ADD_COLLECTION_COVERAGE"] + "(%s, %s, %s, %s, %s, %s, \
                              %s, %s, %s, %s, %s, \
                              %s, %s, %s, %s, %s, %s, %s, \
                              %s, %s, %s, %s, %s, \
                              %s, %s, %s);",
                              (
                                parent_uuid, metadata_uuid, coll_name, coll_title_en, coll_title_fr, coll_desc_en,
                                coll_desc_fr, keywords_en, keywords_fr, coll_crs, provider_type,
                                provider_name, extent_bbox, extent_crs, extent_temporal_begin, extent_temporal_end, geom_wkt, geom_crs,
                                link_type, link_rel, link_title, link_href, link_hreflang,
                                cov_data, format_name, format_mimetype,
                              )
                            )

            conn.commit()
            return True


    def delete_collection(self, coll_name: str):
        """
        Deletes a collection to the database.
        """

        # Connect to the database
        with self.open_conn() as conn:
            # Open a cursor
            result = [0]
            with conn.cursor() as cur:
                # Call the stored procedure
                cur.execute("CALL " + config.DB_STORED_PROCS["DELETE_COLLECTION"] + "(%s, %s);", 
                              (
                                coll_name, 0,
                              )
                            )

                # Read result
                result = cur.fetchone()

            conn.commit()
            return result[0] >= 1

