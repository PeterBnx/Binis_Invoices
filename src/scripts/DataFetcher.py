from pathlib import Path
from Product import Product
from Order import Order
from requests import Session
from bs4 import BeautifulSoup
from re import compile
from lxml import etree
import pandas as pd
import io
import os
from dotenv import load_dotenv
from DB import DB
import sys

class DataFetcher:
    def __init__(self):
        script_dir = Path(__file__).resolve().parent
        project_root = script_dir.parent.parent
        env_path = project_root / '.env'
        load_dotenv(dotenv_path=env_path)

        self.db = DB()

        self.emp_login_url = f"https://www.emporiorologion.gr/admin/controlloaccesso.php"
        self.emp_orders_page_url = f"https://www.emporiorologion.gr/admin/ordini2.php?statoordine=-1&nome=&ordine=&cliente=&referenza=&ups=&datachiusura=&Payment=0&annullato=0&nazione_ordine=-1&ordine_pronto=2&warning=2&marca=-1&primo_ordine=2&pagato=2&API=2&chiavi_in_mano=2&vendita_privata=2&datadal=&dataal="
        self.cis_login_url = f"https://live.livecis.gr/live/default.aspx"
        self.cis_items_url = f"https://live.livecis.gr/live/Materials.aspx?tp=%C5%DF%E4%EF%F2"
        self.session = Session()
        self.all_cis_registered_products = []
        self.emp_orders = []

        self.emp_name = os.environ.get('EMP_NAME')
        self.emp_passwd = os.environ.get('EMP_PASSWD')
        self.cis_name = os.environ.get('CIS_NAME')
        self.cis_passwd = os.environ.get('CIS_PASSWD')


        self.emp_orders = []
        self.emp_payload = {
            "login": self.emp_name,
            "password": self.emp_passwd
        }

        self.order_products = []
        self.prod_quantities = []
        self.prod_codes = []
        self.prod_descriptions = []
        self.prod_prices = []
        self.prod_is_registered = []
        self.prod_brands_full = []
        self.prod_brands_short = []
        self.brands_number_of_products = []

        self.shipping_tax = 0
        self.client_afm = -1
        self.client_name = ""

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
        except Exception as e:
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
                0,
                all_cis_registered_codes[i],
                all_cis_registered_descriptions[i],
                all_cis_registered_prices[i],
                True,
                "Any",
                "Any"
            ))
        return len(all_cis_registered_codes) > 0


    def fetch_all_orders(self):
        print(f"DEBUG: Attempting login for user: {self.emp_name}")
        self.reset_session()

        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.emporiorologion.gr/admin/controlloaccesso.php",
            "Origin": "https://www.emporiorologion.gr"
        })


        print("DEBUG: Visiting login page to collect cookies...")
        self.session.get("https://www.emporiorologion.gr/admin/controlloaccesso.php")

        print(f"DEBUG: Attempting login for user: {self.emp_name}")
        login_res = self.session.post(self.emp_login_url, data=self.emp_payload)
        
        print(f"DEBUG: Login POST status: {login_res.status_code}")
    
        if login_res.status_code == 403:
            print("DEBUG: Still getting 403. The site is likely blocking Render's IP address.")
            return False

        print(f"DEBUG: Login POST status: {login_res.status_code}")
        print(f"DEBUG: Current URL after login: {login_res.url}")

        response = self.session.get(self.emp_orders_page_url)
        soup = BeautifulSoup(response.content, "html.parser", from_encoding='windows-1253')

        print(f"DEBUG: Orders page status: {response.status_code}")
        order_pattern = compile(r"ordini3\.php\?ordine=\d+")
        client_pattern = compile(r"clienti3\.php\?&id_cliente=\d+") 
        date_pattern = compile(r'\b\d{2}/\d{2}/\d{4}\b')
        price_pattern = compile(r'€\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?')

        order_codes = soup.find_all("a", href=order_pattern)
        print(f"DEBUG: Found {len(order_codes)} order elements in HTML")
        client_elements = soup.find_all('a', href=client_pattern) 
        date_elements = soup.find_all('td', {'valign': 'TOP', 'align': 'center'}, string=date_pattern) 
        price_elements = soup.find_all('td', {'valign': 'TOP', 'align': 'RIGHT'}, string=price_pattern)

        if len(order_codes) == 0:
            print(f"DEBUG: HTML Snippet: {response.text[:500]}")
            return False
        
        for order, client, date, price in zip(order_codes, client_elements, date_elements, price_elements):
            self.emp_orders.append(Order(
                order.get_text(strip=True),
                client.get_text(strip=True),
                date.get_text(strip=True),
                price.get_text(strip=True).replace('€\xa0', '')
            ))
        return True

    def fetch_order_products_data(self, order_number):
        self.fetch_all_registered_products()

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
                self.prod_is_registered[i],
                self.prod_brands_full[i],
                self.prod_brands_short[i]
            ))

        self.fetch_shipping_tax()
        self.fetch_client_afm()


    # Get Products' Quantities
    def fetch_products_quantities(self):
        self.prod_quantities = []
        quantities = self.soup.find_all('input', attrs={"name": "q_inviati[]", "id": "q_inviati[]"})
        for quantity in quantities:
            quantity_str = quantity.get('value').replace(' ', '')
            if len(quantity_str) > 0:
                self.prod_quantities.append(int(quantity_str))
            else:
                self.prod_quantities.append(0)



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
            self.prod_is_registered.append(any(prod.code == prod_code for prod in self.all_cis_registered_products))


    # Calculate Shipping Tax
    def fetch_shipping_tax(self):
        spedizione_element = self.soup.find('input', id = 'spedizione')
        if spedizione_element:
            spedizione = float(spedizione_element.get('value'))
        else:
            spedizione = 0

        p_dropshipping_element = self.soup.find('input', attrs={'name': 'packing_dropshipping'})
        if p_dropshipping_element:
            p_dropshipping = float(p_dropshipping_element.get('value'))
        else:
            p_dropshipping = 0

        handling_element = self.soup.find('input', attrs={'name': 'handling'})
        if handling_element:
            handling = float(handling_element.get('value'))
        else:
            handling = 0

        assicurazione_element = self.soup.find('input', attrs={'name': 'assicurazione'})
        if assicurazione_element:
            assicurazione = float(assicurazione_element.get('value'))
        else:
            assicurazione = 0

        maggiorazione_element = self.soup.find('input', attrs={'name': 'maggiorazione'})
        if maggiorazione_element:
            maggiorazione = float(maggiorazione_element.get('value'))
        else:
            maggiorazione = 0

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
            "WATCH" : "Ρολόι",
            "EYE" : "Γυαλιά",
            "JEW" : "Κόσμημα",
            "SUNGLASS" : "Γυαλιά",
            "GLASS": "Γυαλιά",
            "GOGGLES": "Γυαλιά"
        }

        all_brands = self.db.get_all_db_brands()
        self.db.db_connection.commit()
        brands_dict = {brand[0]: brand[1] for brand in all_brands}
        brands_elements = self.soup.find_all(class_ = 'Stile11')

        self.fetch_brands_number_of_products()

        # initializing brands_full, brands_short and brands_types
        brands_full = []
        brands_short = []
        brands_types = []
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
            is_watch = True
            for type in types_dict.keys():
                if type in brand_name_full:
                    brands_types.append(types_dict[type])
                    is_watch = False
                    break
            if (is_watch):
                brands_types.append('Ρολόι')
                
        curr_prod_index = 0
        for i, brand_num in enumerate(self.brands_number_of_products):
            counter = 0
            while (counter < brand_num):
                # If product is registered update the value of brand_short in DB (and temp dictionary) or insert a new
                # one if the brand_full does not exist at all
                if (self.prod_is_registered[curr_prod_index]):
                    target_code = self.prod_codes[curr_prod_index]

                    index = next(
                        (i for i, p in enumerate(self.all_cis_registered_products) 
                        if p.code == target_code), 
                        -1
                    )
                    descr = self.all_cis_registered_products[index].description
                    brand_type = descr.split()[0] # get type of registered product
                    brand_short = ' '.join(descr.split()[1:]) # get brand short
                    brands_types[i] = brand_type
                    brands_short[i] = brand_short

                    brand_found_db = brands_dict.get(brands_full[i])
                    
                    if (brand_found_db and brand_found_db != brand_short):
                        self.db.update_db_brand(brands_full[i], brand_short)
                    elif (not brand_found_db):
                        self.db.insert_db_brand(brands_full[i], brand_short)

                    brands_dict.update({brands_full[i] : brand_short})                        

                description = brands_types[i] + ' ' + brands_short[i]
                self.prod_descriptions.append(description)
                self.prod_brands_full.append(brands_full[i])
                self.prod_brands_short.append(brands_short[i])
                counter += 1
                curr_prod_index += 1

    # Get Client AFM
    def fetch_client_afm(self):
        url_elements = self.soup.find_all('a', limit=7)
        client_url_href = url_elements[-1].get('href') # Simplified index
        client_url = 'https://www.emporiorologion.gr/admin/' + client_url_href
        client_page = self.session.get(client_url)
        client_soup = BeautifulSoup(client_page.content, 'html.parser')
        afm_input = client_soup.find('input', attrs={'id': 'nome222'})
        name_input = client_soup.find('input', attrs={'id': 'nome'})
        
        if afm_input:
            self.client_afm = afm_input.get('value')
        else:
            print(client_soup.prettify())

        if name_input:
            self.client_name = name_input.get('value')
        else:
            print(client_soup.prettify())

    # UTILS

    # e.g. xpath = /html/body/form/center/table[2]/tr[1]/th/span then returns 1 (tr[1])
    def xpath_to_tr_index(self, xpath: str):
        for word in xpath.split('/'):
            if 'tr[' in word:
                word = word.replace('tr[', '')
                word = word.replace(']', '')
                index = int(word)
                return index


def main():
    data_fetcher = DataFetcher()
    data_fetcher.fetch_order_products_data(sys.argv[1])
    data_fetcher.db_connection.close()
    print(data_fetcher.client_name)

if __name__=="__main__":
    main()