from flask import Blueprint

commonconfig = Blueprint('commonconfig', __name__)

from . import views, forms, errors
