from flask import Blueprint

scanconfig = Blueprint('scanconfig', __name__)

from . import views, forms, errors
