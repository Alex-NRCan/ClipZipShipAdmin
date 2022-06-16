"""
This module offers functions to encrypt/verify passwords.
"""

# 3rd party imports
import bcrypt


def get_hashed_password(plain_text_password):
    # Redirect
    return _get_hashed_password(plain_text_password.encode('utf-8'))


def check_password(plain_text_password, hashed_password):
    # Redirect
    return _check_password(plain_text_password.encode('utf-8'), hashed_password)


def _get_hashed_password(plain_text_password):
    # Hash a password for the first time
    #   (Using bcrypt, the salt is saved into the hash itself)
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())


def _check_password(plain_text_password, hashed_password):
    # Check hashed password. Using bcrypt, the salt is saved into the hash itself
    return bcrypt.checkpw(plain_text_password, hashed_password)
