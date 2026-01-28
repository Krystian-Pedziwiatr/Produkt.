from flask import Blueprint


variants_bp = Blueprint('variants', __name__, template_folder='templates', static_folder='static',  url_prefix='/variants')

from . import routes

