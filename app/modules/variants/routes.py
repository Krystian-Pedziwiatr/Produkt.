from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from . import variants_bp
from app import db
from app.models import Product, Variant, Settings
from app.modules.settings.routes import get_setting, generate_variant_urls

# -----------------------------------------------------
# LISTA WARIANTÓW DLA PRODUKTU
# -----------------------------------------------------
@variants_bp.route('/variants/products-list')
@login_required
def variants_products_list():
    """
    Wyświetla listę produktów + liczba wariantów każdego produktu.
    """
    products = Product.query.order_by(Product.created_at.desc()).all()

    # Dodaj liczbę wariantów do każdego obiektu
    for p in products:
        p.variant_count = len(p.variants)

    return render_template('variants_list.html', products=products)


# -----------------------------------------------------
# DODAJ WARIANT
# -----------------------------------------------------
@variants_bp.route('/product/<int:product_id>/variants/add', methods=['GET', 'POST'])
@login_required
def add_variant(product_id):
    from app.models import Product, Variant

    product = Product.query.get_or_404(product_id)
    base_url = get_setting("base_url", "https://weneve.com/img/cms/files/")

    if request.method == "POST":
        color = request.form.get("color")
        folder = request.form.get("folder", "").strip()
        prefix = request.form.get("prefix", "").strip()
        suffixes_raw = request.form.get("suffixes", "").strip()

        # DODATKOWE LINKI OPCJONALNE
        link_url = request.form.get("link_url") or None
        link2_url = request.form.get("link2_url") or None
        link3_url = request.form.get("link3_url") or None
        link4_url = request.form.get("link4_url") or None
        link5_url = request.form.get("link5_url") or None

        # Walidacja obowiązkowych pól
        if not color or not folder or not prefix or not suffixes_raw:
            flash("Kolor, folder, prefix i suffixy są wymagane.", "danger")
            return redirect(url_for("variants.add_variant", product_id=product_id))

        suffixes = [s.strip() for s in suffixes_raw.split(",") if s.strip()]

        # GENEROWANIE OBRAZKÓW
        image_urls = []
        for suf in suffixes:
            url = f"{base_url}{folder}{prefix}{suf}.jpg"
            image_urls.append(url)

        # Uzupełnienie do 10 pól NULL-ami
        while len(image_urls) < 10:
            image_urls.append(None)

        new_variant = Variant(
            color=color,
            image_url=image_urls[0],
            image2_url=image_urls[1],
            image3_url=image_urls[2],
            image4_url=image_urls[3],
            image5_url=image_urls[4],
            image6_url=image_urls[5],
            image7_url=image_urls[6],
            image8_url=image_urls[7],
            image9_url=image_urls[8],
            image10_url=image_urls[9],
            # LINKI OPCJONALNE
            link_url=link_url,
            link2_url=link2_url,
            link3_url=link3_url,
            link4_url=link4_url,
            link5_url=link5_url,
            product_id=product_id
        )

        db.session.add(new_variant)
        db.session.commit()

        flash("Wariant został dodany!", "success")
        return redirect(url_for("variants.variants_products_list", product_id=product_id))

    return render_template("variants_add.html", product=product, base_url=base_url)



# -----------------------------------------------------
# EDYTUJ WARIANT (FORMULARZ + ZAPIS)
# -----------------------------------------------------
@variants_bp.route('/edit/product/<int:product_id>/variant', methods=['GET', 'POST'])
@login_required
def edit_variant(product_id):
    product = Product.query.get_or_404(product_id)
    variants = Variant.query.filter_by(product_id=product_id).all()

    if request.method == "POST":
        variant_id = request.form.get("variant_id")

        if not variant_id:
            flash("Nie wybrano wariantu.", "danger")
            return redirect(request.url)

        variant = Variant.query.filter_by(
            id=variant_id,
            product_id=product_id
        ).first_or_404()

        # ===== ZDJĘCIA =====
        IMAGE_FIELDS = [
            "image_url",
            *[f"image{i}_url" for i in range(2, 11)]
        ]

        for field in IMAGE_FIELDS:
            val = request.form.get(field, "").strip()
            setattr(variant, field, val or None)

        # ===== LINKI =====
        for i in range(1, 6):
            field = "link_url" if i == 1 else f"link{i}_url"
            val = request.form.get(field, "").strip()
            setattr(variant, field, val or None)

        db.session.commit()
        flash("Wariant został zaktualizowany.", "success")

        return redirect(
            url_for("variants.edit_variant", product_id=product_id)
        )

    # ===== GET =====
    return render_template(
        "variants_edit.html",
        product=product,
        variants=variants
    )

# -----------------------------------------------------
# EDYTUJ WARIANT – JSON (FETCH)
# -----------------------------------------------------
@variants_bp.route("/variant/<int:variant_id>/json", methods=["GET"])
@login_required
def variant_json(variant_id):
    variant = Variant.query.get_or_404(variant_id)

    return jsonify({
        "images": {
            "image_url": variant.image_url,
            "image2_url": variant.image2_url,
            "image3_url": variant.image3_url,
            "image4_url": variant.image4_url,
            "image5_url": variant.image5_url,
            "image6_url": variant.image6_url,
            "image7_url": variant.image7_url,
            "image8_url": variant.image8_url,
            "image9_url": variant.image9_url,
            "image10_url": variant.image10_url,
        },
        "links": {
            "link_url": variant.link_url,
            "link2_url": variant.link2_url,
            "link3_url": variant.link3_url,
            "link4_url": variant.link4_url,
            "link5_url": variant.link5_url,
        }
    })


# -----------------------------------------------------
# USUŃ WARIANT
# -----------------------------------------------------
@variants_bp.route('/product/<int:product_id>/variants/<int:variant_id>/delete', methods=['POST'])
@login_required
def delete_variant(product_id, variant_id):
    """
    Usuwa wskazany wariant dla produktu. Operacja jest nieodwracalna —
    przed wykonaniem powinien być potwierdzający modal / confirm() po stronie frontendu.
    """
    variant = Variant.query.filter_by(id=variant_id, product_id=product_id).first_or_404()
    db.session.delete(variant)
    db.session.commit()
    flash('Wariant został usunięty.', 'success')
    return redirect(url_for('variants.variants_products_list', product_id=product_id))
