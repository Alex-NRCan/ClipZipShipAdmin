# 3rd party imports
from flask import Blueprint

# Create the routes BluePrint
routes = Blueprint('routes', __name__)

# Fast import
from .rt_web import *
from .rt_web_admin import *
