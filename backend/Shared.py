from backend.pathResolver import PathResolver
from requests import Session

class Shared:
    def __init__(self):
        self.login_url = 'https://www.emporiorologion.gr/admin/controlloaccesso.php'
        self.orders_page_url = 'https://www.emporiorologion.gr/admin/ordini2.php?statoordine=-1&nome=&ordine=&cliente=&referenza=&ups=&datachiusura=&Payment=0&annullato=0&nazione_ordine=-1&ordine_pronto=2&warning=2&marca=-1&primo_ordine=2&pagato=2&API=2&chiavi_in_mano=2&vendita_privata=2&datadal=&dataal='
        with open(PathResolver.get_creds_path(), 'r') as file:
            creds = [line.strip() for line in file.readlines()]

        self.emp_name = creds[0]
        self.emp_passwd = creds[1]
        self.cis_name = creds[2]
        self.cis_password = creds[3]

        self.payload = {
            'login': self.emp_name,
            'password': self.emp_passwd
        }

        self.session = Session()

shared_instance = Shared()