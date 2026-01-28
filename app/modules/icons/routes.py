from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required
from . import icons_bp
from app.models import Icon
from app import db


# -----------------------------------------------------
# LISTA IKON – PANEL ADMINA (HTML)
# -----------------------------------------------------
@icons_bp.route('/manage')
@login_required
def manage():
    icons = Icon.query.order_by(Icon.id.desc()).all()
    categories = sorted({icon.category for icon in icons if icon.category})
    return render_template('manage.html', icons=icons, categories=categories)


# -----------------------------------------------------
# DODAWANIE IKONY – FORMULARZ (GET + POST)
# -----------------------------------------------------
@icons_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_icon():

    if request.method == 'POST':
        name = request.form.get('name')
        url = request.form.get('url')
        category = request.form.get('category')

        if not name or not url:
            flash("Nazwa i URL są wymagane!", "danger")
            return redirect(url_for('icons.add_icon'))

        new_icon = Icon(name=name, url=url, category=category)
        db.session.add(new_icon)
        db.session.commit()

        flash("Ikona została dodana!", "success")
        return redirect(url_for('icons.manage'))

    return render_template('add.html')


# -----------------------------------------------------
# EDYCJA IKONY – FORMULARZ (GET + POST)
# -----------------------------------------------------
@icons_bp.route('/edit/<int:icon_id>', methods=['GET', 'POST'])
@login_required
def edit_icon(icon_id):
    icon = Icon.query.get_or_404(icon_id)

    if request.method == 'POST':
        icon.name = request.form.get('name')
        icon.url = request.form.get('url')
        icon.category = request.form.get('category')

        if not icon.name or not icon.url:
            flash("Nazwa i URL są wymagane!", "danger")
            return redirect(url_for('icons.edit_icon', icon_id=icon_id))

        db.session.commit()
        flash("Ikona została zaktualizowana!", "success")
        return redirect(url_for('icons.manage'))

    return render_template('edit.html', icon=icon)


# -----------------------------------------------------
# USUWANIE IKONY (HTML BUTTON)
# -----------------------------------------------------
@icons_bp.route('/delete/<int:icon_id>', methods=['POST'])
@login_required
def delete_icon(icon_id):
    icon = Icon.query.get_or_404(icon_id)
    db.session.delete(icon)
    db.session.commit()

    flash("Ikona została usunięta!", "success")
    return redirect(url_for('icons.manage'))


# -----------------------------------------------------
# API – LISTA IKON (JSON)
# -----------------------------------------------------
@icons_bp.route('/api/list')
def api_list_icons():
    category = request.args.get('category')
    query = Icon.query

    if category:
        query = query.filter_by(category=category)

    icons = query.order_by(Icon.id.desc()).all()
    return jsonify([i.to_dict() for i in icons])


# -----------------------------------------------------
# API – USUNIĘCIE IKONY (AJAX)
# -----------------------------------------------------
@icons_bp.route('/api/delete/<int:icon_id>', methods=['DELETE'])
@login_required
def api_delete_icon(icon_id):
    icon = Icon.query.get_or_404(icon_id)
    db.session.delete(icon)
    db.session.commit()
    return jsonify({"status": "deleted", "id": icon_id})
