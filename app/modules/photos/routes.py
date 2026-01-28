from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
from . import photos_bp
from app import db
from app.models import  Settings
from app.modules.settings.routes import get_setting
import os
import io
from PIL import Image
from werkzeug.utils import secure_filename



# -----------------------------------------------------
# LISTA ZDJĘĆ
# -----------------------------------------------------
@photos_bp.route('/list', methods=['GET', 'POST'])
@login_required
def list_photos():

    PHOTOS_STATIC_DIR = os.path.join(
        current_app.root_path,
        "modules",
        "photos",
        "static",
        "uploads"
    )

    RESIZED_DIR = os.path.join(PHOTOS_STATIC_DIR, "resized")
    os.makedirs(RESIZED_DIR, exist_ok=True)

    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}

    def allowed_file(filename):
        return (
            filename
            and not filename.startswith(".")
            and "." in filename
            and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
        )

    # ===== LISTA PRZESKALOWANYCH ZDJĘĆ =====
    files = [
        f for f in os.listdir(RESIZED_DIR)
        if allowed_file(f)
    ]

    return render_template(
        "photos_list.html",
        files=files
    )

# -----------------------------------------------------
# RESIZE ZDJĘĆ
# -----------------------------------------------------
@photos_bp.route('/resize', methods=['GET', 'POST'])
@login_required
def resize():

    import io

    PIL_FORMATS = {
        "jpg": "JPEG",
        "jpeg": "JPEG",
        "png": "PNG",
        "webp": "WEBP"
    }

    BASE_DIR = os.path.join(
        current_app.root_path,
        "modules",
        "photos",
        "static",
        "uploads"
    )

    TMP_DIR = os.path.join(BASE_DIR, "tmp")
    RESIZED_DIR = os.path.join(BASE_DIR, "resized")

    os.makedirs(TMP_DIR, exist_ok=True)
    os.makedirs(RESIZED_DIR, exist_ok=True)

    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}

    def allowed_file(filename):
        return (
            filename
            and not filename.startswith(".")
            and "." in filename
            and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
        )

    if request.method == "POST":
        files = request.files.getlist("photos")

        if not files or files[0].filename == "":
            flash("Nie wybrano żadnych plików.", "danger")
            return redirect(request.url)

        # ===== NAZWA BAZOWA =====
        base_name = request.form.get("base_name", "").strip()
        if not base_name:
            flash("Podaj bazową nazwę plików.", "danger")
            return redirect(request.url)

        base_name = secure_filename(base_name)

        # ===== USTAWIENIA Z BAZY =====
        width = int(get_setting("photos_width", 1200))
        height = int(get_setting("photos_height", 1200))
        keep_ratio = get_setting("photos_keep_ratio", "1") == "1"
        keep_extension = get_setting("photos_keep_extension", "0") == "1"

        max_size_kb = int(get_setting("photos_max_size_kb", 2048))
        quality_start = int(get_setting("photos_quality", 80))
        image_format = get_setting("photos_format", "webp").lower()

        processed = 0
        index = 1

        for file in files:
            if not allowed_file(file.filename):
                continue

            # ===== WCZYTANIE =====
            img = Image.open(file).convert("RGBA")

            # ===== SKALOWANIE =====
            if keep_ratio:
                img.thumbnail((width, height), Image.Resampling.LANCZOS)
            else:
                img = img.resize((width, height), Image.Resampling.LANCZOS)

            # ===== CANVAS =====
            canvas = Image.new("RGBA", (width, height), (255, 255, 255, 255))
            canvas.paste(
                img,
                ((width - img.width) // 2, (height - img.height) // 2)
            )

            # ===== FORMAT =====
            out_ext = image_format
            if keep_extension:
                out_ext = file.filename.rsplit(".", 1)[1].lower()

            if out_ext in ("jpg", "jpeg"):
                canvas = canvas.convert("RGB")

            buffer = io.BytesIO()

            # ===== PNG (bezstratny) =====
            if out_ext == "png":
                canvas.save(
                    buffer,
                    format=PIL_FORMATS[out_ext],
                    optimize=True
                )
                output_bytes = buffer.getvalue()

            # ===== JPG / WEBP =====
            else:
                quality = quality_start
                output_bytes = None

                while quality >= 40:
                    buffer = io.BytesIO()

                    save_kwargs = {"optimize": True, "quality": quality}
                    if out_ext == "webp":
                        save_kwargs["method"] = 6

                    canvas.save(
                        buffer,
                        format=PIL_FORMATS[out_ext],
                        **save_kwargs
                    )

                    if buffer.tell() / 1024 <= max_size_kb:
                        output_bytes = buffer.getvalue()
                        break

                    quality -= 5

                if output_bytes is None:
                    output_bytes = buffer.getvalue()

            # ===== NAZWA PLIKU =====
            suffix = f"-{index}" if index > 1 else ""
            output_name = f"{base_name}{suffix}.{out_ext}"
            output_path = os.path.join(RESIZED_DIR, output_name)

            with open(output_path, "wb") as f:
                f.write(output_bytes)

            processed += 1
            index += 1

        flash(f"Przeskalowano {processed} zdjęć.", "success")
        return redirect(url_for("photos.list_photos"))

    return render_template("photos_resizer.html")



# -----------------------------------------------------
# USTAWIENIA ZDJĘĆ (GET + POST)
# -----------------------------------------------------
@photos_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():

    def _save_setting(key, value):
        setting = Settings.query.filter_by(key=key).first()
        if setting:
            setting.value = str(value)
        else:
            db.session.add(Settings(key=key, value=str(value)))

    if request.method == "POST":

        try:
            # ===== WYMIARY =====
            width_raw = request.form.get("width", "")
            height_raw = request.form.get("height", "")

            if not width_raw.isdigit() or not height_raw.isdigit():
                raise ValueError("Wymiary muszą być liczbami.")

            width = int(width_raw)
            height = int(height_raw)

            if not (100 <= width <= 5000 and 100 <= height <= 5000):
                raise ValueError("Wymiary zdjęcia muszą być w zakresie 100–5000 px.")

            # ===== ROZMIAR / JAKOŚĆ =====
            max_size_raw = request.form.get("max_size_kb", "")
            quality_raw = request.form.get("quality", "")

            if not max_size_raw.isdigit() or not quality_raw.isdigit():
                raise ValueError("Rozmiar pliku i jakość muszą być liczbami.")

            max_size_kb = int(max_size_raw)
            quality = int(quality_raw)

            if not (50 <= max_size_kb <= 10240):
                raise ValueError("Maksymalny rozmiar pliku musi być w zakresie 50–10240 kB.")

            if not (40 <= quality <= 95):
                raise ValueError("Jakość kompresji musi być w zakresie 40–95%.")

            # ===== FORMAT =====
            image_format = request.form.get("image_format")
            if image_format not in {"jpg", "png", "webp"}:
                raise ValueError("Nieprawidłowy format obrazu.")

            # ===== BOOL =====
            keep_ratio = "1" if "keep_ratio" in request.form else "0"
            keep_extension = "1" if "keep_extension" in request.form else "0"

        except ValueError as e:
            flash(str(e), "danger")
            return redirect(url_for("photos.settings"))

        # ===== ZAPIS DO BAZY =====
        _save_setting("photos_width", width)
        _save_setting("photos_height", height)
        _save_setting("photos_max_size_kb", max_size_kb)
        _save_setting("photos_quality", quality)
        _save_setting("photos_format", image_format)
        _save_setting("photos_keep_ratio", keep_ratio)
        _save_setting("photos_keep_extension", keep_extension)

        db.session.commit()

        flash("Ustawienia zdjęć zapisane.", "success")
        return redirect(url_for("photos.settings"))

    # ===== GET =====
    return render_template(
        'photos_settings.html',
        width=get_setting("photos_width", 1200),
        height=get_setting("photos_height", 1200),
        keep_ratio=get_setting("photos_keep_ratio", "1") == "1",
        max_size_kb=get_setting("photos_max_size_kb", 2048),
        quality=get_setting("photos_quality", 80),
        image_format=get_setting("photos_format", "webp"),
        keep_extension=get_setting("photos_keep_extension", "0") == "1"
    )


# -----------------------------------------------------
# USUWANIE PRZESKALOWANYCH ZDJĘĆ
# -----------------------------------------------------
@photos_bp.route("/clear-resized", methods=["POST"])
@login_required
def clear_resized():

    resized_dir = os.path.join(
        current_app.root_path,
        "modules",
        "photos",
        "static",
        "uploads",
        "resized"
    )

    if not os.path.exists(resized_dir):
        flash("Folder przeskalowanych zdjęć nie istnieje.", "warning")
        return redirect(url_for("photos.settings"))

    removed = 0

    for filename in os.listdir(resized_dir):
        file_path = os.path.join(resized_dir, filename)

        # usuwamy TYLKO pliki (żadnych katalogów)
        if os.path.isfile(file_path):
            os.remove(file_path)
            removed += 1

    flash(f"Usunięto {removed} przeskalowanych zdjęć.", "success")
    return redirect(url_for("photos.settings"))

# -----------------------------------------------------
# USUWANIE PLIKÓW TYMCZASOWYCH (TMP)
# -----------------------------------------------------
@photos_bp.route("/clear-tmp", methods=["POST"])
@login_required
def clear_tmp():

    tmp_dir = os.path.join(
        current_app.root_path,
        "modules",
        "photos",
        "static",
        "uploads",
        "tmp"
    )

    if not os.path.exists(tmp_dir):
        flash("Folder tymczasowy nie istnieje.", "warning")
        return redirect(url_for("photos.settings"))

    removed = 0

    for filename in os.listdir(tmp_dir):
        file_path = os.path.join(tmp_dir, filename)

        if os.path.isfile(file_path):
            os.remove(file_path)
            removed += 1

    flash(f"Usunięto {removed} plików tymczasowych.", "success")
    return redirect(url_for("photos.settings"))
