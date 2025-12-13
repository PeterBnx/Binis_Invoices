from backend.Shared import shared_instance
from playwright.sync_api import sync_playwright


class ProductsRegister:
    def register(self, products_data_fetcher):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, channel='chrome')
            page = browser.new_page()
            page.goto("https://live.livecis.gr/live/")

            page.fill('input#MainContent_txtunm', shared_instance.cis_name)
            page.fill('input#MainContent_txtPwd', shared_instance.cis_passwd)
            page.click('input[id=MainContent_Button1]')

            page.goto('https://live.livecis.gr/live/Materials.aspx?tp=%C5%DF%E4%EF%F2')
            page.locator('#MainContent_Button1').click()

            for i in range(len(products_data_fetcher.prod_codes)):
                page.wait_for_load_state('load')
                if (not products_data_fetcher.prod_is_registered[i]):
                    page.fill('input#MainContent_Code', products_data_fetcher.prod_codes[i])
                    page.fill('input#MainContent_Descr', products_data_fetcher.prod_descriptions[i])
                    page.locator('#MainContent_TabContainer1_TabPanel1_Bmu').select_option('ΤΕΜ')
                    page.fill('input#MainContent_TabContainer1_TabPanel1_WSPPrice', products_data_fetcher.prod_prices[i])
                    page.locator('#MainContent_Innext').click()

                    products_data_fetcher.prod_is_registered[i] = True

            browser.close()