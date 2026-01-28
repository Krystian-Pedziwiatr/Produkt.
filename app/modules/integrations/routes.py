from flask import render_template
from flask_login import login_required
from . import integrations_bp




@integrations_bp.route('/api', methods=['GET', 'POST'])
@login_required
def api():


    return render_template(
        "integrations_api.html"
    )


@integrations_bp.route('/import-export', methods=['GET', 'POST'])
@login_required
def import_export():


    return render_template(
        "import_export.html"
    )
