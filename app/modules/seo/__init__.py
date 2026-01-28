from flask import Blueprint


seo_bp = Blueprint('seo', __name__, template_folder='templates', static_folder='static',  url_prefix='/seo')

from . import routes

