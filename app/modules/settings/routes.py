from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user
from oci.identity_domains.models import Settings
from flask_bcrypt import Bcrypt
from . import settings_bp
from app.models import Settings, User
from app import db




@settings_bp.route('/shop', methods=['GET', 'POST'])
@login_required
def shop_settings():
    # pobierz rekord ustawienia
    base_url_setting = Settings.query.filter_by(key="base_url").first()

    if request.method == 'POST':
        new_base_url = request.form.get("base_url", "").strip()

        if not new_base_url:
            flash("BASE URL nie może być puste.", "danger")
            return redirect(url_for("settings.settings_panel"))

        if base_url_setting:
            base_url_setting.value = new_base_url
        else:
            base_url_setting = Settings(key="base_url", value=new_base_url)
            db.session.add(base_url_setting)

        db.session.commit()

        flash("Ustawienia zostały zapisane.", "success")
        return redirect(url_for("settings.shop_settings"))

    return render_template(
        "shop_settings.html",
        base_url=base_url_setting.value if base_url_setting else ""
    )

# -----------------------------------------------------
# FUNKCJE POMOCNICZE
# -----------------------------------------------------

def get_setting(key: str, default=None):
    """
    Pobiera wartość ustawienia z tabeli Setting.
    Lazy import, aby uniknąć cyklicznych importów.
    """
    from app.models import Settings
    row = Settings.query.filter_by(key=key).first()
    return row.value if row else default


def normalize_folder(folder: str) -> str:
    if not folder:
        return ""
    cleaned = folder.strip().strip('/')
    return cleaned + '/' if cleaned else ''


def generate_variant_urls(base_url: str, folder: str, prefix: str, suffixes: list, ext: str = '.jpg'):
    """
    Tworzy pełne URL-e na podstawie:
    BASE_URL + folder + prefix + suffix + '.jpg'
    """
    if base_url and not base_url.endswith('/'):
        base_url = base_url + '/'

    folder_norm = normalize_folder(folder)

    urls = []
    for s in suffixes:
        suf = str(s).strip()
        if not suf:
            continue
        full_url = f"{base_url}{folder_norm}{prefix}{suf}{ext}"
        urls.append(full_url)

    return urls


# -----------------------------------------------------
# USTAWIENIA KONTA — DANE UŻYTKOWNIKA
# -----------------------------------------------------
@settings_bp.route('/account', methods=['GET', 'POST'])
@login_required
def account_settings():
    user = current_user

    if request.method == 'POST':
        new_username = request.form.get('username', '').strip()

        if not new_username:
            flash("Nazwa użytkownika nie może być pusta.", "danger")
            return redirect(url_for('settings.account_settings'))

        # sprawdzenie unikalności
        existing_user = User.query.filter_by(username=new_username).first()

        if existing_user and existing_user.id != user.id:
            flash("Ta nazwa użytkownika jest już zajęta.", "danger")
            return redirect(url_for('settings.account_settings'))

        user.username = new_username
        db.session.commit()

        flash("Nazwa użytkownika została zaktualizowana.", "success")
        return redirect(url_for('settings.account_settings'))

    return render_template('account_settings.html')

# -----------------------------------------------------
# ZMIANA HASŁA UŻYTKOWNIKA
# -----------------------------------------------------


bcrypt = Bcrypt()

@settings_bp.route('/account/password', methods=['POST'])
@login_required
def change_password():
    user = current_user

    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    if not current_password or not new_password or not confirm_password:
        flash("Wszystkie pola są wymagane.", "danger")
        return redirect(url_for('settings.account_settings'))

    if not bcrypt.check_password_hash(user.password, current_password):
        flash("Obecne hasło jest nieprawidłowe.", "danger")
        return redirect(url_for('settings.account_settings'))

    if new_password != confirm_password:
        flash("Nowe hasła nie są identyczne.", "danger")
        return redirect(url_for('settings.account_settings'))

    user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    db.session.commit()

    flash("Hasło zostało zmienione.", "success")
    return redirect(url_for('settings.account_settings'))

# -----------------------------------------------------
# USUWANIE UŻYTKOWNIKA
# -----------------------------------------------------

@settings_bp.route('/account/delete', methods=['POST'])
@login_required
def delete_account():
    password = request.form.get('password')

    if not password:
        flash("Musisz podać hasło.", "danger")
        return redirect(url_for('settings.account_settings'))

    # pobierz PRAWDZIWY obiekt z bazy
    user = User.query.get(current_user.id)

    if not user:
        flash("Użytkownik nie istnieje.", "danger")
        return redirect(url_for('main.login'))

    if not bcrypt.check_password_hash(user.password, password):
        flash("Nieprawidłowe hasło.", "danger")
        return redirect(url_for('settings.account_settings'))

    logout_user()              # wylogowanie
    db.session.delete(user)
    db.session.commit()

    flash("Konto zostało trwale usunięte.", "success")
    return redirect(url_for('main.login'))