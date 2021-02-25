from flask import Blueprint

target = Blueprint('target', __name__)

from . import views, forms, errors
