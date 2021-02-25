from flask import Blueprint

fileleak = Blueprint('fileleak', __name__)

from . import views, forms, errors
