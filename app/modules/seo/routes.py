from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from . import seo_bp
from app.models import Product
import re
from bs4 import BeautifulSoup
from collections import Counter


# -----------------------------------------------------
# LISTA WARIANTÓW DLA PRODUKTU
# -----------------------------------------------------
@seo_bp.route('/description-choice', methods=['GET'])
@login_required
def form():
    products = Product.query.order_by(Product.name).all()

    return render_template(
        'seo_form.html',
        products=products,
        selected_product=None
    )


import re
from bs4 import BeautifulSoup
from collections import Counter
import math


def analyze_seo(description_html, keywords_raw, options):
    soup = BeautifulSoup(description_html, 'html.parser')

    # =====================
    # STRUKTURA HTML
    # =====================
    headings_h1 = soup.find_all('h1')
    headings_h2 = soup.find_all('h2')
    headings_h3 = soup.find_all('h3')

    headings = headings_h1 + headings_h2 + headings_h3 if options['headings'] else []
    lists = soup.find_all('li') if options['lists'] else []
    paragraphs = soup.find_all('p')

    # =====================
    # TEKST GŁÓWNY
    # =====================
    text = soup.get_text(separator=' ')
    text = re.sub(r'\s+', ' ', text).strip().lower()

    words = re.findall(r'\b\w+\b', text)
    word_count = len(words)

    first_100_words = words[:100] if options['first_words'] else []

    # =====================
    # KEYWORDS
    # =====================
    keywords = [
        k.strip().lower()
        for k in re.split(r',|\n', keywords_raw)
        if k.strip()
    ]

    keyword_stats = []
    keyword_score = 0

    for keyword in keywords:
        kw_words = keyword.split()
        kw_len = len(kw_words)

        occurrences = 0
        positions = []

        for i in range(len(words) - kw_len + 1):
            if words[i:i + kw_len] == kw_words:
                occurrences += 1
                positions.append(i)

        density = (occurrences / word_count * 100) if word_count else 0

        # --- kontekst ---
        in_first_100 = any(pos < 100 for pos in positions)
        in_headings = keyword in " ".join(h.get_text().lower() for h in headings)

        # --- ocena keyworda ---
        status = 'bad'
        points = 0

        if occurrences == 0:
            status = 'bad'
        elif 0.3 <= density <= 2.0:
            status = 'good'
            points = 10
        elif density > 2.0:
            status = 'warn'
            points = 5
        else:
            status = 'warn'
            points = 4

        if in_first_100:
            points += 3
        if in_headings:
            points += 4

        keyword_score += points

        keyword_stats.append({
            'keyword': keyword,
            'count': occurrences,
            'density': round(density, 2),
            'in_first_100': in_first_100,
            'in_headings': in_headings,
            'status': status
        })

    # =====================
    # CZYTELNOŚĆ (proxy pod UX)
    # =====================
    sentences = re.split(r'[.!?]', text)
    sentences = [s for s in sentences if len(s.strip()) > 0]
    avg_sentence_length = word_count / len(sentences) if sentences else 0

    readability_score = 0
    if 8 <= avg_sentence_length <= 20:
        readability_score = 10
    elif avg_sentence_length <= 25:
        readability_score = 6
    else:
        readability_score = 2

    # =====================
    # SCORING GŁÓWNY
    # =====================
    score = 0

    # długość treści (Google lubi wyczerpujące treści)
    if word_count >= 400:
        score += 30
    elif word_count >= 250:
        score += 22
    elif word_count >= 150:
        score += 14
    else:
        score += 6

    # struktura
    if headings_h1:
        score += 8
    if headings_h2 or headings_h3:
        score += 7
    if lists:
        score += 5
    if len(paragraphs) >= 3:
        score += 5

    # czytelność
    score += readability_score

    # keywords (limit – Google nie lubi spamowania)
    score += min(keyword_score, 40)

    score = min(score, 100)

    # =====================
    # OCENA KOŃCOWA
    # =====================
    if score < 40:
        grade = 'Słabe'
    elif score < 65:
        grade = 'Średnie'
    elif score < 85:
        grade = 'Dobre'
    else:
        grade = 'Bardzo dobre'

    return {
        'score': score,
        'grade': grade,
        'word_count': word_count,
        'headings_count': len(headings),
        'lists_count': len(lists),
        'avg_sentence_length': round(avg_sentence_length, 1),
        'keywords': keyword_stats
    }


@seo_bp.route('/result', methods=['POST'])
@login_required
def check():
    product_id = request.form.get('product_id')
    keywords_raw = request.form.get('keywords', '')

    options = {
        'headings': 'check_headings' in request.form,
        'lists': 'check_lists' in request.form,
        'first_words': 'check_first_words' in request.form
    }

    product = Product.query.get(product_id)

    if not product or not product.description_template_pl:
        flash('Brak opisu do analizy', 'danger')
        return redirect(url_for('seo.form'))

    result = analyze_seo(
        description_html=product.description_template_pl,
        keywords_raw=keywords_raw,
        options=options
    )

    return render_template(
        'seo_result.html',
        product=product,
        result=result
    )




