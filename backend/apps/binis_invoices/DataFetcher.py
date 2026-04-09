from .Product import Product
from .Order import Order
from requests import Session
from bs4 import BeautifulSoup
from re import compile
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

        order_codes = soup.find_all("a", href=order_pattern)
        client_elements = soup.findAll('a', href=client_pattern) 
        date_elements = soup.findAll('td', {'valign': 'TOP', 'align': 'center'}, string=date_pattern) 

        if (len(order_codes) == 0): 
            self.creds_correct = False 
            return False 
        
        for i in range(len(order_codes)): 
            order_codes[i] = order_codes[i].get_text(strip=True) 
            client_elements[i] = client_elements[i].get_text(strip=True)
            date_elements[i] = date_elements[i].get_text(strip=True)

            self.emp_orders.append(Order(
                order_codes[i],
                client_elements[i],
                date_elements[i],
                "TEST"
            ))
        return True

shared_instance = DataFetcher()