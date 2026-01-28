from flask import render_template, request, url_for, flash
from flask_login import login_required
from . import descriptions_export_bp
from app.models import Product, Variant


# ============================================
# LISTA PRODUKTÓW DO EKSPORTU
# ============================================
@descriptions_export_bp.route('/products', methods=['GET'])
@login_required
def export_products():
    products = Product.query.order_by(Product.id.desc()).all()

    # Dodaj liczbę wariantów do każdego obiektu
    for p in products:
        p.variant_count = len(p.variants)

    return render_template("export_products_list.html", products=products)


# ============================================
# LISTA WARIANTÓW WYBRANEGO PRODUKTU
# ============================================
@descriptions_export_bp.route('/product/<int:product_id>/variants', methods=['GET'])
@login_required
def product_variants(product_id):
    product = Product.query.get_or_404(product_id)
    variants = Variant.query.filter_by(product_id=product_id).all()

    return render_template(
        "export_variants_list.html",
        product=product,
        variants=variants
    )


# ============================================
# ZWRÓCENIE OPISU (PL LUB EN) Z PODMIANĄ LINKÓW
# ============================================
@descriptions_export_bp.route('/variant/<int:variant_id>/description/<lang>', methods=['GET'])
@login_required
def get_description(variant_id, lang):
    variant = Variant.query.get_or_404(variant_id)
    product = variant.product

    if lang == "pl":
        description = product.description_template_pl
    else:
        description = product.description_template_en

    # Podmiana placeholderów
    replacements = {
        "{{LINK1}}": variant.image_url,
        "{{LINK2}}": variant.image2_url,
        "{{LINK3}}": variant.image3_url,
        "{{LINK4}}": variant.image4_url,
        "{{LINK5}}": variant.image5_url,
        "{{LINK6}}": variant.image6_url,
        "{{LINK7}}": variant.image7_url,
        "{{LINK8}}": variant.image8_url,
        "{{LINK9}}": variant.image9_url,
        "{{LINK10}}": variant.image10_url,
    }

    for key, val in replacements.items():
        if val:
            description = description.replace(key, val)

    return description
