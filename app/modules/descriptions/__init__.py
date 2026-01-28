from flask import Blueprint


descriptions_bp = Blueprint('descriptions', __name__, template_folder='templates', static_folder='static',  url_prefix='/descriptions')

from . import routes

