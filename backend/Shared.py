from backend.pathResolver import PathResolver
from requests import Session
from bs4 import BeautifulSoup
from urllib.parse import quote

greek = "Είδος"  # this is what the encoded bytes represent
encoded = quote(greek, encoding="cp1253")



class Shared:
    def __init__(self):
        self.emp_login_url = f"https://www.emporiorologion.gr/admin/controlloaccesso.php"
        self.emp_orders_page_url = f"https://www.emporiorologion.gr/admin/ordini2.php?statoordine=-1&nome=&ordine=&cliente=&referenza=&ups=&datachiusura=&Payment=0&annullato=0&nazione_ordine=-1&ordine_pronto=2&warning=2&marca=-1&primo_ordine=2&pagato=2&API=2&chiavi_in_mano=2&vendita_privata=2&datadal=&dataal="
        self.cis_login_url = f"https://live.livecis.gr/live/default.aspx"
        self.cis_items_url = f"https://live.livecis.gr/live/Materials.aspx?tp=%C5%DF%E4%EF%F2"
        with open(PathResolver.get_creds_path(), 'r') as file:
            creds = [line.strip() for line in file.readlines()]

        self.emp_name = creds[0]
        self.emp_passwd = creds[1]
        self.cis_name = creds[2]
        self.cis_password = creds[3]
        self.session = Session()

        self.emp_payload = {
            'login': self.emp_name,
            'password': self.emp_passwd
        }

        r = self.session.get(self.cis_login_url)
        soup = BeautifulSoup(r.text, 'html.parser')

        self.cis_payload = {
            "__VIEWSTATE": soup.find(id="__VIEWSTATE").get("value", ""),
            "__VIEWSTATEGENERATOR": soup.find(id="__VIEWSTATEGENERATOR").get("value", ""),
            "__EVENTVALIDATION": soup.find(id="__EVENTVALIDATION").get("value", ""),
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",

            "ctl00$MainContent$txtunm": self.cis_name,
            "ctl00$MainContent$txtPwd": self.cis_password,

            'ctl00$MainContent$Button1': 'Login'
        }

shared_instance = Shared()