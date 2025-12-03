import requests
from bs4 import BeautifulSoup
from pathResolver import PathResolver

class ProductsDataFetcher:
    def __init__(self):
        self.login_url = 'https://www.emporiorologion.gr/admin/controlloaccesso.php'
        self.order_url = 'https://www.emporiorologion.gr/admin/ordini3.php?ordine='

    input_order = input('Αριθμός Παραγγελίας: ')

    order_url += input_order

    credsPath = PathResolver.getCredsPath()
    creds = open(credsPath, 'r+').readlines()
    for i in range(len(creds)):
        creds[i] = creds[i].replace('\n', '')

    emp_name = creds[0]
    emp_passwd = creds[1]
    cis_name = creds[2]
    cis_password = creds[3]

    payload = {
        'login': emp_name,
        'password': emp_passwd
    }

    prod_quantities = []
    prod_codes = []
    prod_prices = []


    with requests.session() as s:
        s.post(login_url, data=payload)
        r = s.get(order_url)
        soup = BeautifulSoup(r.content, 'html.parser')



    #Get Products' Quantities
    quantities = soup.find_all('input', attrs={"name": "q_inviati[]", "id": "q_inviati[]"})

    for quantity in quantities:
        prod_quantities.append(quantity.get('value').replace(' ', ''))



    #Get Products' Codes
    codes_names = soup.find_all(class_ = 'Stile3')

    for code_name in codes_names:
        soup_codes = BeautifulSoup(str(code_name), 'html.parser')
        code = soup_codes.find('font')
        prod_codes.append(code.text.replace(' ', ''))



    #Get Products' Prices
    prices = soup.find_all('td', align="RIGHT", limit=len(prod_codes)*3)

    for i in range(2, (len(prices)), 3):
        prod_prices.append(prices[i].get_text().replace('€ ', ''))



    #Calculate Shipping Tax
    spedizione_element = soup.find('input', id = 'spedizione')
    spedizione = float(spedizione_element.get('value'))

    p_dropshipping_element = soup.find('input', attrs={'name': 'packing_dropshipping'})
    p_dropshipping = float(p_dropshipping_element.get('value'))

    handling_element = soup.find('input', attrs={'name': 'handling'})
    handling = float(handling_element.get('value'))

    assicurazione_element = soup.find('input', attrs={'name': 'assicurazione'})
    assicurazione = float(assicurazione_element.get('value'))

    maggiorazione_element = soup.find('input', attrs={'name': 'maggiorazione'})
    maggiorazione = float(maggiorazione_element.get('value'))

    shipping_tax = round((spedizione + p_dropshipping + handling + assicurazione + maggiorazione), 2)


    #Get Client AFM
    url_elements = soup.find_all('a', limit=7)
    client_url_href = url_elements[len(url_elements) - 1].get('href')

    client_url = 'https://www.emporiorologion.gr/admin/' + client_url_href

    client_page = s.get(client_url)
    client_soup = BeautifulSoup(client_page.content, 'html.parser') 
    client_afm = client_soup.find('input', attrs={'id': 'nome222'}).get('value')