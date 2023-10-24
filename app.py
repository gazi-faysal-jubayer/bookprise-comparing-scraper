from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    x = request.form['bookname']
    final = []
    final = []

    wafi = requests.get(f'https://www.wafilife.com/search/?wpsolr_q={x}').text
    soup = BeautifulSoup(wafi, 'lxml')
    book_names = soup.find_all('h3', class_='heading-title product-title')
    writers = soup.find_all('div', class_='wd_product_categories')
    wafi_prices = soup.find_all('span', class_='price')
    images = soup.find_all('div', class_='product-image-front')
    wafi_links = soup.find_all('div', class_='product_thumbnail_wrapper')
    book_name_list = []
    writer_list = []
    image_list = []
    wafi_price_list = []
    wafi_link_list = []
    rokomari_price_list = []
    rokomari_Link_list = []
    for book in book_names:
        book_name_list.append(book.text.strip())
    for writer in writers:
        writer_list.append(writer.text.strip())
    for image in images:
        image_list.append(image.img['src'])
    for price in wafi_prices:
        p = price.span.text
        wafi_price_list.append(p)
    for link in wafi_links:
        wafi_link_list.append(link.a['href'])

    for i in range(len(book_name_list)):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }
        rokomari = requests.get(f'https://www.rokomari.com/search?term={book_name_list[i]}&search_type=ALL', headers=headers).text
        time.sleep(5)
        soupR = BeautifulSoup(rokomari, 'lxml')
        rBooks = soupR.find_all('div', class_='book-list-wrapper')
        rWritters = soupR.find_all('p', class_='book-author')
        rPrices = soupR.find_all('p', class_='book-price')
        rLinks = soupR.find_all('div', class_='books-wrapper__item')
        rBookList = []
        rWriterList = []
        rPriceList = []
        rLinkList = []
        for rB in rBooks:
            rBookList.append(rB.h4.text)
        for rW in rWritters:
            rWriterList.append(rW.text)
        for rP in rPrices:
            rPriceList.append(rP.text.split()[-1] + '৳')
        for rlink in rLinks:
            rLinkList.append('https://www.rokomari.com' + rlink.a['href'])

        key = 0
        for j in range(len(rBookList)):
            rBookList_replaced = rBookList[j].replace("ী", "ি").replace("ূ", "ু")
            book_name_list_replaced = book_name_list[i].replace("ী", "ি").replace("ূ", "ু")
            rWriterList_replaced = rWriterList[j].replace("ী", "ি").replace("ূ", "ু")
            writer_list_replaced = writer_list[i].replace("ী", "ি").replace("ূ", "ু")
            if rBookList_replaced in book_name_list_replaced or book_name_list_replaced in rBookList_replaced:
                if rWriterList_replaced in writer_list_replaced or writer_list_replaced in rWriterList_replaced:
                    rokomari_price_list.append(rPriceList[j])
                    rokomari_Link_list.append(rLinkList[j])
                    key = 1
                    break
        if key == 0:
            rokomari_price_list.append('Not available')
            rokomari_Link_list.append('Not available')

        final_result = {
            'Sl no': i + 1,
            'Book name': book_name_list[i],
            'Writer': writer_list[i],
            'Image': image_list[i],
            'Price in WifiLife': wafi_price_list[i],
            'Wafilife Link': wafi_link_list[i],
            'Price in Rokomari': rokomari_price_list[i],
            'Rokomari Link': rokomari_Link_list[i]
        }

        final.append(final_result)
    return render_template('results.html', results=final)

if __name__ == '__main__':
    app.run(debug=True)
