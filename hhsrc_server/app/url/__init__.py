from flask import Blueprint

url = Blueprint('url', __name__)

from . import views, forms, errors
