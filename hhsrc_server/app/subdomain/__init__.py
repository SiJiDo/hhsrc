from flask import Blueprint

subdomain = Blueprint('subdomain', __name__)

from . import views, forms, errors
