from flask import render_template, jsonify
from flask_login import login_required
from . import descriptions_bp
from flask import session, request, redirect, url_for, flash
from app import db
from ...models import Product, Variant



@descriptions_bp.route('/product', methods=['GET', 'POST'])
@login_required
def action_select():
    return render_template('action_select.html')

import re
from flask import flash, render_template, request, redirect, url_for, session
from sqlalchemy import func

@descriptions_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_product():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        sku = request.form.get('sku', '').strip()
        ean = request.form.get('ean', '').strip() or None

        # Podstawowa walidacja pustych pól
        if not name or not sku:
            flash('Nazwa produktu i SKU są wymagane.', 'danger')
            return render_template('create.html', name=name, sku=sku, ean=ean)


        # Sprawdzenie unikalności SKU
        existing_sku = Product.query.filter_by(sku=sku).first()
        if existing_sku:
            flash('Produkt z podanym SKU już istnieje w bazie.', 'danger')
            return render_template('create.html', name=name, sku=sku, ean=ean)

        # Sprawdzenie unikalności nazwy (case-insensitive)
        existing_name = Product.query.filter(func.lower(Product.name) == name.lower()).first()
        if existing_name:
            flash('Produkt o takiej nazwie już istnieje. Sprawdź nazwę lub zmień ją.', 'danger')
            return render_template('create.html', name=name, sku=sku, ean=ean)

        # --- ZAPIS DO SESJI (tylko gdy walidacje przeszły) ---
        session['product_data'] = {
            'name': name,
            'sku': sku,
            'ean': ean
        }

        # Przejście do kreatora opisu (etap 2)
        return redirect(url_for('descriptions.create_description'))

    # GET → Pobierz dane z sesji (jeśli user wrócił)
    product_data = session.get('product_data', {})
    return render_template('create.html', **product_data)


@descriptions_bp.route('/create/description', methods=['GET', 'POST'])
@descriptions_bp.route('/edit/description/<int:product_id>', methods=['GET', 'POST'])
@login_required
def create_description(product_id=None):

    # =================================================
    # TRYB EDYCJI ISTNIEJĄCEGO PRODUKTU
    # =================================================
    if product_id is not None:
        product = Product.query.get_or_404(product_id)

        if request.method == 'POST':
            description_pl = request.form.get('description', '').strip()

            if not description_pl:
                flash("Opis nie może być pusty.", "danger")
                return redirect(
                    url_for('descriptions.create_description', product_id=product.id)
                )

            product.description_template_pl = description_pl
            db.session.commit()

            flash("Opis PL został zaaktualizowany.", "success")
            return redirect(
                url_for('descriptions.create_description_en', product_id=product.id)
            )

        # GET – edycja
        return render_template(
            'create_description.html',
            mode='edit',
            product_id=product.id,
            description=product.description_template_pl or ''
        )

    # =================================================
    # TRYB TWORZENIA NOWEGO PRODUKTU (SESJA)
    # =================================================
    product_data = session.get('product_data')

    if not product_data:
        flash("Najpierw uzupełnij podstawowe dane produktu.", "danger")
        return redirect(url_for('descriptions.create_product'))

    if request.method == 'POST':
        description_pl = request.form.get('description', '').strip()

        if not description_pl:
            flash("Opis nie może być pusty.", "danger")
            return redirect(url_for('descriptions.create_description'))

        product_data['description_pl'] = description_pl
        session['product_data'] = product_data

        flash("Opis PL zapisany tymczasowo.", "success")
        return redirect(url_for('descriptions.create_description_en'))

    # GET – tworzenie
    return render_template(
        'create_description.html',
        mode='create',
        product_id=None,
        description=product_data.get('description_pl', '')
    )




@descriptions_bp.route('/create/description-en', methods=['GET', 'POST'])
@login_required
def create_description_en():
    product_id = request.args.get('product_id', type=int)
    product_data = session.get('product_data')

    product = None
    if product_id is not None:
        product = Product.query.get_or_404(product_id)

    # =================================================
    # POST
    # =================================================
    if request.method == 'POST':
        description_en = request.form.get('description', '').strip()

        if not description_en:
            flash("Opis EN nie może być pusty.", "danger")
            return redirect(
                url_for('descriptions.create_description_en', product_id=product_id)
            )

        # -------- EDYCJA ISTNIEJĄCEGO --------
        if product:
            product.description_template_en = description_en
            db.session.commit()

            flash("Opis został zaaktualizowany", "success")
            return redirect(url_for('descriptions.product_list'))

        # -------- TWORZENIE NOWEGO --------
        if not product_data:
            flash("Brak danych produktu w sesji.", "danger")
            return redirect(url_for('descriptions.create_product'))

        new_product = Product(
            name=product_data['name'],
            sku=product_data['sku'],
            ean=product_data.get('ean'),
            description_template_pl=product_data.get('description_pl', ''),
            description_template_en=description_en
        )

        db.session.add(new_product)
        db.session.commit()

        session.pop('product_data', None)

        flash("Produkt został zapisany.", "success")
        return redirect(url_for('descriptions.product_list'))

    # =================================================
    # GET
    # =================================================
    return render_template(
        'create_description_en.html',
        product_id=product.id if product else None,
        description_pl=(
            product.description_template_pl if product
            else (product_data or {}).get('description_pl', '')
        ),
        description_en=(
            product.description_template_en if product
            else (product_data or {}).get('description_en', '')
        )
    )



@descriptions_bp.route('/products')
@login_required
def product_list():
    products = Product.query.order_by(Product.created_at.desc()).all()

    # Dodaj liczbę wariantów do każdego obiektu
    for p in products:
        p.variant_count = len(p.variants)

    return render_template('list.html', products=products)


@descriptions_bp.route('/products/delete/<int:product_id>', methods=['POST'])
@login_required
def product_delete(product_id):
    product = Product.query.get_or_404(product_id)

    # Usuwamy produkt + warianty (bo masz cascade)
    db.session.delete(product)
    db.session.commit()

    flash("Produkt został usunięty.", "success")
    return redirect(url_for('descriptions.product_list'))


@descriptions_bp.route('/variants')
@login_required
def create_variants():
    return render_template('variants.html')

