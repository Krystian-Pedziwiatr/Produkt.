from flask import Blueprint


integrations_bp = Blueprint('integrations', __name__, template_folder='templates', static_folder='static',  url_prefix='/integrations')

from . import routes

