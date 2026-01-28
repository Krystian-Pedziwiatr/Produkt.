from flask import Blueprint


photos_bp = Blueprint('photos', __name__, template_folder='templates', static_folder='static',  url_prefix='/photos')

from . import routes

