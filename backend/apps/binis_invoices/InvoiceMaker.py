from playwright.sync_api import sync_playwright
from django.http import StreamingHttpResponse
from time import sleep, time
import json
from .Shared import Shared

invoice_type_dict = {
    'tda' : 'ΤΔΑ',
    'inve' : 'INVE'
}

class InvoiceMaker:
    def __init__(self):
        self.unregistered_products = []

        

    def make_invoice(self, products_data_fetcher, invoice_type):
        
        shared_instance = Shared()
        with sync_playwright() as p:
            self.browser = p.chromium.launch(headless=True)                
            page = self.browser.new_page()
            page.goto("https://live.livecis.gr/live/")

            page.fill('input#MainContent_txtunm', shared_instance.cis_name)
            page.fill('input#MainContent_txtPwd', shared_instance.cis_passwd)
            page.click('input[id=MainContent_Button1]')

            page.goto('https://live.livecis.gr/live/Document.aspx?action=N&Personaa=&tp=%d0%d9%cb%c7%d3%c5%c9%d3')

            #Select invoice type
            page.locator('#MainContent_TabContainer1_TabPanel1_DocType').select_option(invoice_type_dict[invoice_type])
            if (invoice_type == 'inve'):
                page.locator('#MainContent_TabContainer1_TabPanel1_MDVatExe').select_option('14')

            #Select client
            page.locator('#MainContent_TabContainer1_TabPanel1_Button6').click()
            print(products_data_fetcher.client_afm)
            page.locator('#MainContent_GridView1').locator(f"tr:has-text('{products_data_fetcher.client_afm}')").click()

            page.reload()

            index = 0
            while index < len(products_data_fetcher.prod_codes):

                if index % 35 == 0:
                    page.reload()

                while(products_data_fetcher.prod_quantities[index] == 0):
                    index += 1

                page.locator('#MainContent_Button2').click()

                while not page.locator('#MainContent_LLinkid_DDD_PW-1').is_visible():
                    page.locator('#MainContent_LLinkid_I').click()

                page.locator('#MainContent_LLinkid_I').fill(products_data_fetcher.prod_codes[index])

                #find from dropdown
                dropdown_codes = page.locator('#MainContent_LLinkid_DDD_PW-1').get_by_text(products_data_fetcher.prod_codes[index]).all()
                dropdown_prices = page.locator('#MainContent_LLinkid_DDD_L_LBI0T3').all()

                start_dropdown_searching_time = time()
                while len(dropdown_codes) == 0 and time() - start_dropdown_searching_time < 3:
                    dropdown_codes = page.locator('#MainContent_LLinkid_DDD_PW-1').get_by_text(products_data_fetcher.prod_codes[index]).all()
                    dropdown_prices = page.locator('#MainContent_LLinkid_DDD_L_LBI0T3').all()

                if len(dropdown_prices) == 0:
                    page.locator('#MainContent_ImageButton1').click()
                    self.unregistered_products.append(products_data_fetcher.prod_codes[index])
                    yield f"data: {json.dumps({'type': 'SKIPPED', 'code': products_data_fetcher.prod_codes[index]})}\n\n"
                    index += 1
                    continue
                
                correct_code_string = len(products_data_fetcher.prod_codes[index])
                dropdown_code_selection = products_data_fetcher.prod_codes[index]
                dropdown_price_selection = products_data_fetcher.prod_prices[index]
                for i in range(len(dropdown_codes)):
                    if len(dropdown_codes[i].inner_text()) == correct_code_string:
                        dropdown_code_selection = dropdown_codes[i]
                        correct_code_string = dropdown_codes[i].inner_text()
                        dropdown_price_selection = dropdown_prices[i].inner_text()
                        
                dropdown_code_selection.click()


                #price
                if dropdown_price_selection == '0.00':
                    sleep(2)
                    page.locator('#igtxtMainContent_Lprice').clear()
                    page.locator('#igtxtMainContent_Lprice').fill(products_data_fetcher.prod_prices[index])
                else:
                    while page.locator('#igtxtMainContent_Lprice').get_attribute('value') == '0,00':
                        pass
                    page.locator('#igtxtMainContent_Lprice').clear()
                    page.locator('#igtxtMainContent_Lprice').fill(products_data_fetcher.prod_prices[index])


                #temaxia
                page.locator('#igtxtMainContent_Lquant').fill(str(products_data_fetcher.prod_quantities[index]))

                #plus
                page.locator('#MainContent_ImageButton1').click()
                
                # for react
                yield f"data: {json.dumps({'type': 'COMPLETE', 'code': products_data_fetcher.prod_codes[index]})}\n\n"
                
                index += 1

            #metaforika
            page.locator('#MainContent_BtnServ').click()

            while not page.locator('#MainContent_LLinkid0_DDD_PW-1').is_visible():
                page.locator('#MainContent_LLinkid0_B-1').click()
            page.locator('#MainContent_LLinkid0_DDD_L_LBI5T0').click()
            sleep(1)

            page.locator('#igtxtMainContent_Lprice0').fill(str(products_data_fetcher.shipping_tax).replace('.', ','))
            page.locator('#igtxtMainContent_Lquant0').fill('1')
            page.locator('#MainContent_BtLineIN').click()
            sleep(1)
            page.locator('#MainContent_Button5').click()
            page.screenshot(path="/app/shared_data/invoice.png", full_page=True)
            yield f"data: {json.dumps({'type': 'FINISHED'})}\n\n"
            self.browser.close()


    def close_browser(self):
        self.browser.close()