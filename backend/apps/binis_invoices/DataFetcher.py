from .Product import Product
from .Order import Order
from .models import Brand
from requests import Session
from bs4 import BeautifulSoup
from re import compile
from lxml import etree
import pandas as pd
import io


class DataFetcher:

    def __init__(self):
        self.emp_login_url = f"https://www.emporiorologion.gr/admin/controlloaccesso.php"
        self.emp_orders_page_url = f"https://www.emporiorologion.gr/admin/ordini2.php?statoordine=-1&nome=&ordine=&cliente=&referenza=&ups=&datachiusura=&Payment=0&annullato=0&nazione_ordine=-1&ordine_pronto=2&warning=2&marca=-1&primo_ordine=2&pagato=2&API=2&chiavi_in_mano=2&vendita_privata=2&datadal=&dataal="
        self.cis_login_url = f"https://live.livecis.gr/live/default.aspx"
        self.cis_items_url = f"https://live.livecis.gr/live/Materials.aspx?tp=%C5%DF%E4%EF%F2"
        self.session = Session()
        self.all_cis_registered_products = []
        self.emp_orders = []

        self.order_products = []
        self.prod_quantities = []
        self.prod_codes = []
        self.prod_prices = []
        self.prod_is_registered = []
    

    def reset_session(self):
        try:
            self.session.close()
        except:
            pass
        self.session = Session()

    def _load_cis_tokens(self):
        r = self.session.get(self.cis_login_url)
        soup = BeautifulSoup(r.text, "html.parser")

        return {
            "__VIEWSTATE": soup.find(id="__VIEWSTATE").get("value", ""),
            "__VIEWSTATEGENERATOR": soup.find(id="__VIEWSTATEGENERATOR").get("value", ""),
            "__EVENTVALIDATION": soup.find(id="__EVENTVALIDATION").get("value", "")
        }
    
    def get_value(self, name, soup):
        tag = soup.find("input", {"name": name})
        return tag["value"] if tag else ""


    def fetch_all_registered_products(self):
        self.reset_session()
        self.all_cis_registered_products = []
        tokens = self._load_cis_tokens()
        login_payload = {
            **tokens,
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "ctl00$MainContent$txtunm": self.cis_name,
            "ctl00$MainContent$txtPwd": self.cis_passwd,
            "ctl00$MainContent$Button1": "Login"
        }
        self.session.post(
            self.cis_login_url,
            data=login_payload
        )

        items_page = self.session.get(self.cis_items_url)
        soup = BeautifulSoup(items_page.text, "html.parser")
        export_payload = {
            "__EVENTTARGET": "ctl00$MainContent$gv1$imgExport",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": self.get_value("__VIEWSTATE", soup),
            "__VIEWSTATEGENERATOR": self.get_value("__VIEWSTATEGENERATOR", soup),
            "__EVENTVALIDATION": self.get_value("__EVENTVALIDATION", soup)
        }
        export_response = self.session.post(self.cis_items_url, data=export_payload)
        try:
            df = pd.read_excel(io.BytesIO(export_response.content))
        except Exception:
            self.all_cis_registered_products = []
            return False

        all_cis_registered_codes = [
            str(item).strip() for item in df.get("Κωδικός", [])
        ]
        all_cis_registered_descriptions = [
            str(item).strip() for item in df.get("Περιγραφή", [])
        ]
        all_cis_registered_prices = [
            str(item).strip() for item in df.get("Τιμή Χονδρικής", [])
        ]

        for i in range(len(all_cis_registered_codes)):
            self.all_cis_registered_products.append(Product(
                all_cis_registered_codes[i],
                all_cis_registered_descriptions[i],
                all_cis_registered_prices[i],
                True
            ))
        return len(all_cis_registered_codes) > 0


    def fetch_all_orders(self):


        self.reset_session()
        self.emp_orders = []
        self.emp_payload = {
            "login": self.emp_name,
            "password": self.emp_passwd
        }

        self.session.post(
            self.emp_login_url,
            data=self.emp_payload
        )

        response = self.session.get(self.emp_orders_page_url)
        soup = BeautifulSoup(response.text, "html.parser")

        order_pattern = compile(r"ordini3\.php\?ordine=\d+")
        client_pattern = compile(r"clienti3\.php\?&id_cliente=\d+") 
        date_pattern = compile(r'\b\d{2}/\d{2}/\d{4}\b')
        price_pattern = compile(r'€\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?')

        order_codes = soup.find_all("a", href=order_pattern)
        client_elements = soup.findAll('a', href=client_pattern) 
        date_elements = soup.findAll('td', {'valign': 'TOP', 'align': 'center'}, string=date_pattern) 
        price_elements = soup.findAll('td', {'valign': 'TOP', 'align': 'RIGHT'}, string=price_pattern)

        if (len(order_codes) == 0): 
            self.creds_correct = False 
            return False 
        
        for i in range(len(order_codes)): 
            order_codes[i] = order_codes[i].get_text(strip=True) 
            client_elements[i] = client_elements[i].get_text(strip=True)
            date_elements[i] = date_elements[i].get_text(strip=True)
            price_elements[i] = price_elements[i].get_text(strip=True)

            self.emp_orders.append(Order(
                order_codes[i],
                client_elements[i],
                date_elements[i],
                price_elements[i]
            ))
        return True
    
    def fetch_order_products_data(self, order_number):
        order_url =  'https://www.emporiorologion.gr/admin/ordini3.php?ordine=' + order_number
        self.session.post(self.emp_login_url, data=self.emp_payload)
        r = self.session.get(order_url)
        self.soup = BeautifulSoup(r.content, 'html.parser')

        self.fetch_products_quantities()
        self.fetch_products_codes()
        self.fetch_products_prices()
        self.fetch_products_is_registered()
        self.fetch_products_descriptions()

        for i in range(len(self.prod_codes)):
            self.order_products.append(Product(
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
        self.prod_quantities = []
        quantities = self.soup.find_all('input', attrs={"name": "q_inviati[]", "id": "q_inviati[]"})
        for quantity in quantities:
            self.prod_quantities.append(int(quantity.get('value').replace(' ', '')))



    # Get Products' Codes
    def fetch_products_codes(self):
        self.prod_codes = []
        codes_names = self.soup.find_all(class_ = 'Stile3')
        for code_name in codes_names:
            soup_codes = BeautifulSoup(str(code_name), 'html.parser')
            code = soup_codes.find('font')
            self.prod_codes.append(code.text.replace(' ', ''))

    # Get Products' Prices
    def fetch_products_prices(self):
        self.prod_prices = []
        prices = self.soup.find_all('td', align="RIGHT", limit=len(self.prod_codes)*3)
        for i in range(2, (len(prices)), 3):
            self.prod_prices.append(prices[i].get_text().replace('€ ', ''))


    # For each item, check if it is registered
    def fetch_products_is_registered(self):
        self.prod_is_registered = []
        for prod_code in self.prod_codes:
            self.prod_is_registered.append(prod_code in self.all_cis_registered_codes)


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

    # getting the number of products for each brand
    # it compares the xpaths of each brand full name and prod code to find which product is assigned to each path
    def fetch_brands_number_of_products(self):
        brands_indexes = []
        prod_code_indexes = []
        root = etree.HTML(str(self.soup))
        tree = etree.ElementTree(root)

        brands_matches = root.xpath("//*[contains(concat(' ', normalize-space(@class), ' '), ' Stile11 ')]")
        codes_matches = root.xpath("//*[contains(concat(' ', normalize-space(@class), ' '), ' Stile3 ')]")

        for match in brands_matches:
            brands_indexes.append(self.xpath_to_tr_index(tree.getpath(match)))
        
        for match in codes_matches:
            prod_code_indexes.append(self.xpath_to_tr_index(tree.getpath(match)))

        for brand in reversed(brands_indexes):
            curr_prods_num = 0
            for prod in reversed(prod_code_indexes):
                if (prod > brand):
                    curr_prods_num += 1
                    prod_code_indexes.pop()
                else:
                    break
            self.brands_number_of_products.append(curr_prods_num)
        self.brands_number_of_products = [num for num in reversed(self.brands_number_of_products)]

    # Formatting products descriptions
    def fetch_products_descriptions(self):
        types_dict = {
            "watch" : "Ρολόι",
            "eye" : "Γυαλιά",
            "jew" : "Κόσμημα",
            "sunglass" : "Γυαλιά Ηλίου",
            "glass": "Γυαλιά Ηλίου"
        }
        # db = DB()

        b = Brand(brand_full="Test Full", brand_display="Test Display")
        b.save()

        all_brands = Brand.objects.all()
        print(all_brands)
        brands_dict = {item[1]: item[2] for item in db.get_all_brands()}
        self.number_of_products = sum(self.prod_quantities)
        brands_elements = self.soup.find_all(class_ = 'Stile11')

        self.fetch_brands_number_of_products()

        # initializing brands_full, brands_short and brands_types
        for element in brands_elements:
            brand_name_full = element.get_text().strip().upper()
            self.brands_descriptions.append(brand_name_full)
            self.brands_full.append(brand_name_full)
            # starting format of brand_short
            if (brand_name_full in self.brands_dict.keys()):
                brand_name_short = self.brands_dict[brand_name_full]
            else: 
                brand_name_short = brand_name_full
            self.brands_short.append(brand_name_short)

            # format the type
            # if a word from types dict is found in brand full name, append the according brand type
            for type in self.types_dict.keys():
                is_watch = True
                if type in brand_name_full:
                    self.brands_types.append(self.types_dict[type])
                    is_watch = False
                    break
                if (is_watch):
                    self.brands_types.append('Ρολόι')
                    break

        curr_prod_index = 0
        for i, brand_num in enumerate(self.brands_number_of_products):
            counter = 0
            while (counter < brand_num):
                # If product is registered update the value of brand_short in DB (and temp dictionary) or insert a new
                # one if the brand_full does not exist at all
                if (self.prod_is_registered[curr_prod_index]):
                    index = self.all_cis_registered_codes.index(self.prod_codes[curr_prod_index])
                    descr = self.all_cis_registered_descriptions[index]

                    brand_type = descr.split()[0] # get type of registered product
                    brand_short = ' '.join(descr.split()[1:]) # get brand short
                    self.brands_types[i] = brand_type
                    self.brands_short[i] = brand_short

                    brand_found_db = db.get_brand_by_brand_full(self.brands_full[i])
                    if (brand_found_db and brand_found_db[2] != brand_short):
                        db.update_brand(self.brands_full[i], brand_short)
                    elif (not brand_found_db):
                        db.insert_brand(self.brands_full[i], brand_short)

                    self.brands_dict.update({self.brands_full[i] : brand_short})                        

                description = self.brands_types[i] + ' ' + self.brands_short[i]
                self.prod_descriptions.append(description)
                self.prod_brands_full.append(self.brands_full[i])
                self.prod_brands_short.append(self.brands_short[i])
                self.prod_types.append(self.brands_types[i])
                counter += 1
                curr_prod_index += 1


    # Get Client AFM
    def fetch_client_afm(self):
        url_elements = self.soup.find_all('a', limit=7)
        client_url_href = url_elements[len(url_elements) - 1].get('href')
        client_url = 'https://www.emporiorologion.gr/admin/' + client_url_href
        client_page = self.session.get(client_url)
        client_soup = BeautifulSoup(client_page.content, 'html.parser') 
        self.client_afm = client_soup.find('input', attrs={'id': 'nome222'}).get('value')

    # UTILS

    # e.g. xpath = /html/body/form/center/table[2]/tr[1]/th/span then returns 1 (tr[1])
    def xpath_to_tr_index(self, xpath: str):
        for word in xpath.split('/'):
            if 'tr[' in word:
                word = word.replace('tr[', '')
                word = word.replace(']', '')
                index = int(word)
                return index