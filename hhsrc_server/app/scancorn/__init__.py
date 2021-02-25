from flask import Blueprint

scancorn = Blueprint('scancorn', __name__)

from . import views, forms, errors
