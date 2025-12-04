from re import compile
from bs4 import BeautifulSoup
from backend.Shared import shared_instance

class OrdersDataFetcher():
    def __init__(self):
        shared_instance.session.post(shared_instance.login_url, data=shared_instance.payload)

        response = shared_instance.session.get(shared_instance.orders_page_url)
        self.soup = BeautifulSoup(response.content, 'html.parser')

        order_pattern = compile(r"ordini3\.php\?ordine=\d+")
        client_pattern = compile(r"clienti3\.php\?&id_cliente=\d+")
        date_pattern = compile(r'\b\d{2}/\d{2}/\d{4}\b')

        self.order_elements = self.soup.findAll('a', href=order_pattern)
        self.client_elements = self.soup.findAll('a', href=client_pattern)
        self.date_elements = self.soup.findAll('td', {'valign': 'TOP', 'align': 'center'}, string=date_pattern)

        for i in range(len(self.order_elements)):
            self.order_elements[i] = self.order_elements[i].get_text(strip=True)
            self.client_elements[i] = self.client_elements[i].get_text(strip=True)
            self.date_elements[i] = self.date_elements[i].get_text(strip=True)