from flask import Blueprint


icons_bp = Blueprint('icons', __name__, template_folder='templates', static_folder='static',  url_prefix='/icons')

from . import routes

