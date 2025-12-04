from Shared import shared_instance
from bs4 import BeautifulSoup
from pathResolver import PathResolver

class ProductsDataFetcher:
    def __init__(self, order_number):
        self.types_dict = {
            "watch" : "Ρολόι",
            "eye" : "Γυαλιά",
            "jew" : "Κόσμημα",
            "sunglass" : "Γυαλιά Ηλίου",
            "glass": "Γυαλιά Ηλίου"
        }
        self.order_number = order_number
        self.order_url =  shared_instance.orders_page_url + self.order_number

        self.prod_quantities = []
        self.prod_codes = []
        self.prod_prices = []

        shared_instance.session.post(shared_instance.login_url, data=shared_instance.payload)
        r = shared_instance.session.get(self.order_url)
        self.soup = BeautifulSoup(r.content, 'html.parser')



    # Get Products' Quantities
    def fetch_products_quantities(self):
        quantities = self.soup.find_all('input', attrs={"name": "q_inviati[]", "id": "q_inviati[]"})

        for quantity in quantities:
            self.prod_quantities.append(quantity.get('value').replace(' ', ''))



    # Get Products' Codes
    def fetch_products_codes(self):
        codes_names = self.soup.find_all(class_ = 'Stile3')

        for code_name in codes_names:
            soup_codes = BeautifulSoup(str(code_name), 'html.parser')
            code = soup_codes.find('font')
            self.prod_codes.append(code.text.replace(' ', ''))



    # Get Products' Prices
    def fetch_products_prices(self):
        prices = self.soup.find_all('td', align="RIGHT", limit=len(self.prod_codes)*3)

        for i in range(2, (len(prices)), 3):
            self.prod_prices.append(prices[i].get_text().replace('€ ', ''))



    # Calculate Shipping Tax
    def fetch_shipping_tax(self):
        spedizione_element = self.soup.find('input', id = 'spedizione')
        spedizione = float(spedizione_element.get('value'))

        p_dropshipping_element = self.soup.find('input', attrs={'name': 'packing_dropshipping'})
        p_dropshipping = float(p_dropshipping_element.get('value'))

        handling_element = self.soup.find('input', attrs={'name': 'handling'})
        handling = float(handling_element.get('value'))

        assicurazione_element = self.soup.find('input', attrs={'name': 'assicurazione'})
        assicurazione = float(assicurazione_element.get('value'))

        maggiorazione_element = self.soup.find('input', attrs={'name': 'maggiorazione'})
        maggiorazione = float(maggiorazione_element.get('value'))

        self.shipping_tax = round((spedizione + p_dropshipping + handling + assicurazione + maggiorazione), 2)


    # Formatting products descriptions
    

    # Get Client AFM
    def fetch_client_afm(self):
        url_elements = self.soup.find_all('a', limit=7)
        client_url_href = url_elements[len(url_elements) - 1].get('href')

        client_url = 'https://www.emporiorologion.gr/admin/' + client_url_href

        client_page = self.requests_session.get(client_url)
        client_soup = BeautifulSoup(client_page.content, 'html.parser') 
        self.client_afm = client_soup.find('input', attrs={'id': 'nome222'}).get('value')