from backend.Shared import shared_instance
from backend.db import DB
from bs4 import BeautifulSoup
from backend.pathResolver import PathResolver
import pandas as pd
import io

class ProductsDataFetcher:
    def __init__(self):
        self.types_dict = {
            "watch" : "Ρολόι",
            "eye" : "Γυαλιά",
            "jew" : "Κόσμημα",
            "sunglass" : "Γυαλιά Ηλίου",
            "glass": "Γυαλιά Ηλίου"
        }

        self.prod_quantities = []
        self.prod_codes = []
        self.prod_prices = []
        self.prod_descriptions = []
        self.prod_is_registered = []


    def fetch_order_products_data(self, order_number):
        self.order_number = order_number
        self.order_url =  'https://www.emporiorologion.gr/admin/ordini3.php?ordine=' + self.order_number
        shared_instance.session.post(shared_instance.emp_login_url, data=shared_instance.emp_payload)
        r = shared_instance.session.get(self.order_url)
        self.soup = BeautifulSoup(r.content, 'html.parser')

        self.fetch_products_quantities()
        self.fetch_products_codes()
        self.fetch_products_prices()
        self.fetch_products_is_registered()
        self.fetch_products_descriptions()
        self.fetch_shipping_tax()
        self.fetch_client_afm()

        self.print_products_data()


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


    # For each item, check if it is registered
    def fetch_products_is_registered(self):
        for prod_code in self.prod_codes:
            self.prod_is_registered.append(prod_code in shared_instance.all_cis_registered_codes)


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
    def fetch_products_descriptions(self): #!!! NEED IMPROVEMENT FOR CREATING DESCRIPTION IF ITEM IS REGISTERED
        db = DB()
        brands_quantities = []
        brands = []
        brands_dict = {item[1]: item[2] for item in db.get_all_brands()}

        # Get brands elements texts
        brands_elements = self.soup.find_all(class_ = 'Stile11')

        values = self.soup.find_all('font', attrs={'size': '2', 'face' : 'trebuchet MS'})

        for code in values:
            if '€' not in code.get_text():
                brands_quantities.append(code.get_text())

        for brand in brands_elements:
            brands.append(brand.get_text())

        #Formatting brands_types (what is the type of every brand in the order)
        brands_types = []
        for i in range(len(brands)):
            is_watch = True
            for type in list(self.types_dict.keys()):
                if type in brands[i].lower():
                    brands_types.append(self.types_dict[type])
                    is_watch = False
                    break
            if is_watch:
                brands_types.append('Ρολόι')

        #Formatting brands list (keeping only the name of the brand) 
        for i in range(len(brands)):
            for name in list(brands_dict.keys()):
                if name in brands[i]:
                    brands[i] = brands_dict[name]
                    break

        #Creating brand_descriptions (the general brand description for its items)
        brand_descriptions = []

        for i in range(len(brands_types)):
            brand_descriptions.append(brands_types[i] + " " + brands[i])


        #Assigning every item to its brand and creating the final description for every item
        j = 0
        for i in range(len(brands_quantities)):
            counter = 0
            
            while (counter + int(self.prod_quantities[j]) <= int(brands_quantities[i])):
                # Searching if item exists in registered products to get the description from there
                try:
                    index = shared_instance.all_cis_registered_codes.index(self.prod_codes[len(self.prod_descriptions)])
                    self.prod_descriptions.append(shared_instance.all_cis_registered_descriptions[index])
                except ValueError:
                    self.prod_descriptions.append(brand_descriptions[i])
                counter += int(self.prod_quantities[j])
                j+=1

                if j == len(self.prod_quantities) - 1:
                    break

        if len(brands_quantities) > 0:
            for u in range(j, len(self.prod_codes)):
                try:
                    index = shared_instance.all_cis_registered_codes.index(self.prod_codes[len(self.prod_descriptions)])
                    self.prod_descriptions.append(shared_instance.all_cis_registered_descriptions[index])
                except ValueError:
                    self.prod_descriptions.append(brand_descriptions[i])
        else:
            for u in range(j, len(self.prod_codes)):
                try:
                    index = shared_instance.all_cis_registered_codes.index(self.prod_codes[len(self.prod_descriptions)])
                    self.prod_descriptions.append(shared_instance.all_cis_registered_descriptions[index])
                except ValueError:
                    self.prod_descriptions.append(brand_descriptions[i])
    

    # Get Client AFM
    def fetch_client_afm(self):
        url_elements = self.soup.find_all('a', limit=7)
        client_url_href = url_elements[len(url_elements) - 1].get('href')

        client_url = 'https://www.emporiorologion.gr/admin/' + client_url_href

        client_page = shared_instance.session.get(client_url)
        client_soup = BeautifulSoup(client_page.content, 'html.parser') 
        self.client_afm = client_soup.find('input', attrs={'id': 'nome222'}).get('value')


        #printing
    def print_products_data(self):
        print('Client AFM:', self.client_afm)
        print('Number of order:', self.order_number)

        for i in range(len(self.prod_codes)):
            if(self.prod_quantities[i] != '0'):
                print('%-5s'%self.prod_quantities[i], '%-20s'%self.prod_codes[i], '%-20s'%self.prod_descriptions[i], '%10s'%self.prod_prices[i], '%5s'%self.prod_is_registered[i])