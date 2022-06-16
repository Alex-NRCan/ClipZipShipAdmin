"""
This class represents a User record in the database.
"""

# Application modules
from core import config


class DBUser(object):
    """
    Class representing a User record in the database.
    """

    def __init__(self, dictcursor):
        self.dictcursor = dictcursor

    def id(self):
        return self.dictcursor[config.DB_TABLE_USERS["FIELD_ID"]]

    def username(self):
        return self.dictcursor[config.DB_TABLE_USERS["FIELD_USERNAME"]]

    def password(self):
        return self.dictcursor[config.DB_TABLE_USERS["FIELD_PASSWORD"]]

    def role(self):
        return self.dictcursor[config.DB_TABLE_USERS["FIELD_ROLE"]]

    def to_json_simple(self):
        return {
            "username": self.username(),
            "role": self.role()
        }

    def __str__(self):
        return "User(id='{id}', username='{username}', role='{role}')".format(id=self.id(),
                                                                              username=self.username(),
                                                                              role=self.role())

