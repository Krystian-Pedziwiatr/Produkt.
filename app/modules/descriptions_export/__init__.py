from flask import Blueprint


descriptions_export_bp = Blueprint('descriptions_export', __name__, template_folder='templates', static_folder='static',  url_prefix='/descriptions-export')

from . import routes

