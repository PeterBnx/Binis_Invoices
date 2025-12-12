from backend.Shared import shared_instance
from backend.db import DB
from backend.Product import Product
from bs4 import BeautifulSoup


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
        self.prod_types = []
        self.prod_brands_full = []
        self.prod_brands_short = []
        self.prod_descriptions = []
        self.prod_is_registered = []

        self.products = []


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

        for i in range(len(self.prod_codes)):
            self.products.append(Product(
                self.prod_quantities[i],
                self.prod_codes[i],
                self.prod_descriptions[i],
                self.prod_prices[i],
                self.prod_is_registered[i]
            ))

        self.fetch_shipping_tax()
        self.fetch_client_afm()

        self.print_products_data()


    # Get Products' Quantities
    def fetch_products_quantities(self):
        quantities = self.soup.find_all('input', attrs={"name": "q_inviati[]", "id": "q_inviati[]"})

        for quantity in quantities:
            self.prod_quantities.append(int(quantity.get('value').replace(' ', '')))



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
    def fetch_products_descriptions(self):
        db = DB()
        brands_elements = self.soup.find_all(class_ = 'Stile11')
        brands_number_of_products = []
        brands_full = []
        brands_short = []
        brands_types = []
        brands_dict = {item[1]: item[2] for item in db.get_all_brands()}
        number_of_products = sum(self.prod_quantities)

        # initializing brands_full, brands_short and brands_types
        for element in brands_elements:
            brand_name_full = element.get_text().strip().upper()
            brands_full.append(brand_name_full)
            # starting format of brand_short
            if (brand_name_full in brands_dict.keys()):
                brand_name_short = brands_dict[brand_name_full]
            else: 
                brand_name_short = brand_name_full
            brands_short.append(brand_name_short)

            # format the type
            # if a word from types dict is found in brand full name, append the according brand type
            for type in self.types_dict.keys():
                is_watch = True
                if type in brand_name_full:
                    brands_types.append(self.types_dict[type])
                    is_watch = False
                    break
                if (is_watch):
                    brands_types.append('Ρολόι')
                    break

        # getting the number of products for each brand
        brands_number_of_products = [int(code.get_text().strip()) for code in self.soup.find_all('font', attrs={'size': '2', 'face' : 'trebuchet MS'}) if '€' not in code.get_text()]
        last_brand_number_of_products = number_of_products - sum(brands_number_of_products)
        brands_number_of_products.append(last_brand_number_of_products) # the last brand

        curr_prod_index = 0
        for i, brand_num in enumerate(brands_number_of_products):
            counter = 0
            while (counter < brand_num):
                # If product is registered update the value of brand_short in DB (and temp dictionary) or insert a new
                # one if the brand_full does not exist at all
                if (self.prod_is_registered[curr_prod_index]):
                    index = shared_instance.all_cis_registered_codes.index(self.prod_codes[len(self.prod_descriptions)])
                    descr = shared_instance.all_cis_registered_descriptions[index]

                    brand_type = descr.split()[0] # get type of registered product
                    brand_short = ' '.join(descr.split()[1:]) # get brand short
                    brands_types[i] = brand_type
                    brands_short[i] = brand_short

                    brand_found_db = db.get_brand_by_brand_full(brands_full[i])
                    if (brand_found_db and brand_found_db[2] != brand_short):
                        db.update_brand(brands_full[i], brand_short)
                    elif (not brand_found_db):
                        db.insert_brand(brands_full[i], brand_short)

                    brands_dict.update({brands_full[i] : brand_short})
                        

                description = brands_types[i] + ' ' + brands_short[i]
                self.prod_descriptions.append(description)
                self.prod_brands_full.append(brands_full[i])
                self.prod_brands_short.append(brands_short[i])
                self.prod_types.append(brands_types[i])
                counter += self.prod_quantities[curr_prod_index]
                curr_prod_index += 1

        print(brands_full)
        print(brands_short)
        print(brands_types)


    # Get Client AFM
    def fetch_client_afm(self):
        url_elements = self.soup.find_all('a', limit=7)
        client_url_href = url_elements[len(url_elements) - 1].get('href')
        client_url = 'https://www.emporiorologion.gr/admin/' + client_url_href
        client_page = shared_instance.session.get(client_url)
        client_soup = BeautifulSoup(client_page.content, 'html.parser') 
        self.client_afm = client_soup.find('input', attrs={'id': 'nome222'}).get('value')


    def reset_fetcher(self):
        self.products.clear()
        self.prod_quantities.clear()
        self.prod_codes.clear()
        self.prod_descriptions.clear()
        self.prod_prices.clear()
        self.prod_is_registered.clear()

        #printing
    def print_products_data(self):
        print('Client AFM:', self.client_afm)
        print('Number of order:', self.order_number)

        for i in range(len(self.prod_codes)):
            if(self.prod_quantities[i] != '0'):
                print('%-5s'%self.prod_quantities[i], '%-20s'%self.prod_codes[i], '%-20s'%self.prod_descriptions[i], '%10s'%self.prod_prices[i], '%5s'%self.prod_is_registered[i])