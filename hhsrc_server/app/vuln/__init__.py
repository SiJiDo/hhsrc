from flask import Blueprint

vuln = Blueprint('vuln', __name__)

from . import views, forms, errors
