import re
import sys
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request
from difflib import SequenceMatcher
from urllib.parse import urljoin, quote
from concurrent.futures import ThreadPoolExecutor

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

app = Flask(__name__)

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    ),
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://www.wafilife.com/'
}


def normalize_text(val):
    if not val:
        return ''
    val = val.lower()
    val = val.replace('ী', 'ি').replace('ূ', 'ু').replace('ণ', 'ন').replace('শ', 'স').replace('ষ', 'স')
    val = re.sub(r'[^\w\s\u0980-\u09FF]', ' ', val)
    return ' '.join(val.split())


def similarity(a, b):
    na, nb = normalize_text(a), normalize_text(b)
    if not na or not nb:
        return 0.0
    if na == nb:
        return 1.0
    return SequenceMatcher(None, na, nb).ratio()


def search_wafilife(query):
    url = f"https://www.wafilife.com/api/search?keyword={quote(query)}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code != 200:
            return []
        data = res.json()
        items = data.get('items', [])
        books = []
        for it in items:
            item_id = str(it.get('id', ''))
            if item_id.startswith(('wri_', 'pub_', 'sub_')) or not it.get('name'):
                continue

            name = it.get('name', '').strip()
            authors = ', '.join(it.get('authors', [])).strip()

            price_field = it.get('sale_price')
            if isinstance(price_field, list) and price_field:
                price_val = price_field[0]
            else:
                price_val = it.get('price')

            price_str = f"{int(price_val)}৳" if price_val else "Price unavailable"
            slug = it.get('slug', '')
            link = f"https://www.wafilife.com/{slug}/pd/{item_id}" if slug and item_id else "Not available"
            img = it.get('image', {}).get('original') or it.get('image', {}).get('thumbnail') or ""

            books.append({
                'title': name,
                'author': authors,
                'price': price_str,
                'link': link,
                'image': img
            })
        return books
    except Exception as exc:
        print(f"Error fetching Wafilife: {exc}")
        return []


def search_rokomari(query):
    url = f"https://www.rokomari.com/search?term={quote(query)}&search_type=ALL"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code != 200:
            return []
        soup = BeautifulSoup(res.text, 'html.parser')
        items = soup.find_all(lambda tag: tag.name == 'div' and any('productGridItem' in c for c in tag.get('class', [])))
        books = []
        for item in items:
            title_el = item.find('p', class_=lambda c: c and 'productTitle' in c)
            author_el = item.find('p', class_=lambda c: c and 'productAuthor' in c)
            price_el = item.find('p', class_=lambda c: c and 'productPrice' in c)
            link_el = item.find('a', href=lambda h: h and '/book/' in h)
            img_el = item.find('img')

            title = title_el.text.strip() if title_el else ''
            author = author_el.text.strip() if author_el else ''
            price = price_el.text.strip() if price_el else 'Not available'
            link = urljoin('https://www.rokomari.com', link_el['href']) if link_el else 'Not available'
            img = img_el.get('data-src') or img_el.get('src') if img_el else ''

            if title:
                books.append({
                    'title': title,
                    'author': author,
                    'price': price,
                    'link': link,
                    'image': img
                })
        return books
    except Exception as exc:
        print(f"Error fetching Rokomari: {exc}")
        return []


def match_book_in_rokomari(wb):
    r_books = search_rokomari(wb['title'])
    best_match = None
    best_score = 0.0

    for rb in r_books:
        t_score = similarity(wb['title'], rb['title'])
        if wb['author'] and rb['author']:
            a_score = similarity(wb['author'], rb['author'])
            total_score = 0.75 * t_score + 0.25 * a_score
        else:
            total_score = t_score

        if total_score > best_score:
            best_score = total_score
            best_match = rb

    if best_match and best_score >= 0.65:
        return best_match['price'], best_match['link']
    return 'Not available', 'Not available'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    x = request.form.get('bookname') or request.args.get('bookname') or ''
    x = x.strip()
    if not x:
        return render_template('results.html', results=[], bookname="")

    final = []
    wafi_books = search_wafilife(x)[:10]

    if wafi_books:
        with ThreadPoolExecutor(max_workers=5) as executor:
            roko_results = list(executor.map(match_book_in_rokomari, wafi_books))

        for i, (wb, (roko_price, roko_link)) in enumerate(zip(wafi_books, roko_results)):
            final_result = {
                'Sl no': i + 1,
                'Book name': wb['title'],
                'Writer': wb['author'],
                'Image': wb['image'],
                'Price in WifiLife': wb['price'],
                'Wafilife Link': wb['link'],
                'Price in Rokomari': roko_price,
                'Rokomari Link': roko_link
            }
            final.append(final_result)
    else:
        roko_books = search_rokomari(x)[:10]
        for i, rb in enumerate(roko_books):
            final_result = {
                'Sl no': i + 1,
                'Book name': rb['title'],
                'Writer': rb['author'],
                'Image': rb['image'],
                'Price in WifiLife': 'Not available',
                'Wafilife Link': 'Not available',
                'Price in Rokomari': rb['price'],
                'Rokomari Link': rb['link']
            }
            final.append(final_result)

    return render_template('results.html', results=final, bookname=x)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
