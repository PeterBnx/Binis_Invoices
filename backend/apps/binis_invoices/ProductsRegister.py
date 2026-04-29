from time import sleep
from .DataFetcher import update_db_brands
import json
import os

class ProductsRegister:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.cis_name = os.environ.get('CIS_NAME')
        self.cis_passwd = os.environ.get('CIS_PASSWD')

    def register(self, order_data):
        products = order_data["products"]
        updated_brands = order_data["updated_brands"]
        prod_codes = [prod['code'] for prod in products]
        prod_is_registered = [prod["isRegistered"] for prod in products]
        prod_prices = [prod['price'] for prod in products]
        prod_descriptions = [prod["description"] for prod in products]

        update_db_brands(updated_brands)

        try:
            from playwright.sync_api import sync_playwright
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=True, args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage', # 👈 Very important for Docker/Render
                '--disable-gpu',
            ])
            page = self.browser.new_page()
            page.goto("https://live.livecis.gr/live/")

            page.fill('input#MainContent_txtunm', self.cis_name)
            page.fill('input#MainContent_txtPwd', self.cis_passwd)
            page.click('input[id=MainContent_Button1]')

            page.goto('https://live.livecis.gr/live/Materials.aspx?tp=%C5%DF%E4%EF%F2')
            page.locator('#MainContent_Button1').click()

            for i in range(len(prod_codes)):
                page.wait_for_load_state('load')
                if (not prod_is_registered[i]):
                    page.fill('input#MainContent_Code', prod_codes[i])
                    page.fill('input#MainContent_Descr', prod_descriptions[i])
                    page.locator('#MainContent_TabContainer1_TabPanel1_Bmu').select_option('ΤΕΜ')
                    page.fill('input#MainContent_TabContainer1_TabPanel1_WSPPrice', prod_prices[i])
                    page.locator('#MainContent_Innext').click()
                    yield f"data: {json.dumps({'type': 'COMPLETE', 'code': prod_codes[i]})}\n\n"
            yield f"data: {json.dumps({'type': 'FINISHED'})}\n\n"

            while True:
                yield f"data: {json.dumps({'type': 'KEEP_ALIVE'})}\n\n"
                sleep(1)

        except Exception as e:
            print(f"Error during invoice making: {e}")
            yield f"data: {json.dumps({'type': 'ERROR', 'message': str(e)})}\n\n"

        finally:
            print("Client disconnected or process finished. Closing browser.")
            self.close_browser()

    def close_browser(self):
        if self.browser:
            self.browser.close()
            self.browser = None
        if self.playwright:
            self.playwright.stop()
            self.playwright = None