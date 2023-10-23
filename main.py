from bs4 import BeautifulSoup
import requests

x = input("Input a book name you want to search: ")
print("Searching.......")

wafi = requests.get(f'https://www.wafilife.com/search/?wpsolr_q={x}').text
soup = BeautifulSoup(wafi, 'lxml')
book_names = soup.find_all('h3', class_='heading-title product-title')
writers = soup.find_all('div', class_='wd_product_categories')
wafi_prices = soup.find_all('span', class_='price')
book_name_list = []
writer_list = []
wafi_price_list = []
rokomari_price_list = []
for book in book_names:
    book_name_list.append(book.text.strip())
for writer in writers:
    writer_list.append(writer.text.strip())
for price in wafi_prices:
    p = price.ins.span.text
    wafi_price_list.append(p)

for i in range(len(book_name_list)):
    rokomari = requests.get(f'https://www.rokomari.com/search?term={book_name_list[i]}&search_type=ALL').text
    soupR = BeautifulSoup(rokomari, 'lxml')
    rokomari_price = soupR.find('p', class_='book-price').text.split()[-1]
    rokomari_price_list.append(rokomari_price + '৳')

    print(f'Sl no: {i+1}')
    print(f'Book name: {book_name_list[i]}')
    print(f'Writer: {writer_list[i]}')
    print(f'Price in WifiLife: {wafi_price_list[i]}')
    print(f'Price in Rokomari: {rokomari_price_list[i]}')

    final_result ={
        'Sl no': i + 1,
        'Book name': book_name_list[i],
        'Writer': writer_list[i],
        'Price in WifiLife': wafi_price_list[i],
        'Price in Rokomari': rokomari_price_list[i]
    }

    # print(final_result)
    print('')







