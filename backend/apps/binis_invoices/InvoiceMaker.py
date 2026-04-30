import os
from time import sleep, time
import json
import signal
from contextlib import contextmanager
from .models import Brand
from .DataFetcher import update_db_brands

class TimeoutException(Exception):
    pass

@contextmanager
def timeout(seconds):
    """Context manager for timeouts"""
    def handler(signum, frame):
        raise TimeoutException("Operation timed out")
    
    # Set the signal handler and alarm
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)  # Disable alarm

class InvoiceMaker:
    def __init__(self):
        self.unregistered_products = []
        self.playwright = None
        self.browser = None
        self.cis_name = os.environ.get('CIS_NAME')
        self.cis_passwd = os.environ.get('CIS_PASSWD')

    def make_invoice(self, order_data):
        products = order_data["products"]
        client_afm = order_data["client_afm"]
        shipping_tax = order_data["shipping_tax"]
        updated_brands = order_data["updated_brands"]
        prod_codes = [prod['code'] for prod in products]
        prod_quantities = [prod['quantity'] for prod in products]
        prod_prices = [prod['price'] for prod in products]
        print(prod_codes)
        
        try:
            update_db_brands(updated_brands)
        except e:
            print(e)

        try:
            from playwright.sync_api import sync_playwright
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=True, args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--single-process'
            ])
            page = self.browser.new_page()
            page.set_default_timeout(15000)  # 15 second timeout for all page actions
            page.set_default_navigation_timeout(15000)  # 15 second navigation timeout
            page.goto("https://live.livecis.gr/live/")

            page.fill('input#MainContent_txtunm', self.cis_name)
            page.fill('input#MainContent_txtPwd', self.cis_passwd)
            page.click('input[id=MainContent_Button1]')

            page.goto('https://live.livecis.gr/live/Document.aspx?action=N&Personaa=&tp=%d0%d9%cb%c7%d3%c5%c9%d3')

            #Select invoice type
            page.locator('#MainContent_TabContainer1_TabPanel1_DocType').select_option('ΠΑΡ')

            #Select client
            page.locator('#MainContent_TabContainer1_TabPanel1_Button6').click()
            page.locator('#MainContent_GridView1').locator(f"tr:has-text('{client_afm}')").click()
            page.reload()

            index = 0
            while index < len(products):

                if index % 35 == 0:
                    page.reload()

                while(prod_quantities[index] == 0):
                    index += 1

                page.locator('#MainContent_Button2').click()

                while not page.locator('#MainContent_LLinkid_DDD_PW-1').is_visible():
                    page.locator('#MainContent_LLinkid_I').click()

                page.locator('#MainContent_LLinkid_I').fill(prod_codes[index])

                #find from dropdown
                dropdown_codes = page.locator('#MainContent_LLinkid_DDD_PW-1').get_by_text(prod_codes[index]).all()
                dropdown_prices = page.locator('#MainContent_LLinkid_DDD_L_LBI0T3').all()

                start_dropdown_searching_time = time()
                while len(dropdown_codes) == 0 and time() - start_dropdown_searching_time < 3:
                    dropdown_codes = page.locator('#MainContent_LLinkid_DDD_PW-1').get_by_text(prod_codes[index]).all()
                    dropdown_prices = page.locator('#MainContent_LLinkid_DDD_L_LBI0T3').all()

                if len(dropdown_prices) == 0:
                    page.locator('#MainContent_ImageButton1').click()
                    self.unregistered_products.append(prod_codes[index])
                    yield f"data: {json.dumps({'type': 'SKIPPED', 'code': prod_codes[index]})}\n\n"
                    index += 1
                    continue
                
                correct_code_string = len(prod_codes[index])
                dropdown_code_selection = prod_codes[index]
                dropdown_price_selection = prod_prices[index]
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
                    page.locator('#igtxtMainContent_Lprice').fill(prod_prices[index])
                else:
                    while page.locator('#igtxtMainContent_Lprice').get_attribute('value') == '0,00':
                        pass
                    page.locator('#igtxtMainContent_Lprice').clear()
                    page.locator('#igtxtMainContent_Lprice').fill(prod_prices[index])


                #temaxia
                page.locator('#igtxtMainContent_Lquant').fill(str(prod_quantities[index]))

                #plus
                page.locator('#MainContent_ImageButton1').click()
                
                # for react
                yield f"data: {json.dumps({'type': 'COMPLETE', 'code': prod_codes[index]})}\n\n"
                
                index += 1

            #metaforika
            page.locator('#MainContent_BtnServ').click()

            while not page.locator('#MainContent_LLinkid0_DDD_PW-1').is_visible():
                page.locator('#MainContent_LLinkid0_B-1').click()
            page.locator('#MainContent_LLinkid0_DDD_L_LBI5T0').click()
            sleep(1)

            page.locator('#igtxtMainContent_Lprice0').fill(str(shipping_tax).replace('.', ','))
            page.locator('#igtxtMainContent_Lquant0').fill('1')
            page.locator('#MainContent_BtLineIN').click()
            sleep(1)
            page.locator('#MainContent_Button5').click()
            sleep(1)
            page.locator('#MainContent_InButon').click()
            sleep(1)
            page.screenshot(path="/app/shared_data/invoice.png", full_page=True)
            yield f"data: {json.dumps({'type': 'FINISHED'})}\n\n"

        except Exception as e:
            print(f"Error during invoice making: {e}")
            yield f"data: {json.dumps({'type': 'ERROR', 'message': str(e)})}\n\n"
        
        finally:
            print("Client disconnected or process finished. Closing browser.")
            self.close_browser()

    def close_browser(self):
        """Close browser with timeout handling to prevent hanging"""
        try:
            if self.browser:
                try:
                    # Set a timeout for browser close operation
                    self.browser.close()
                except TimeoutException:
                    print("Browser close timed out, forcing shutdown")
                except Exception as e:
                    print(f"Error closing browser: {e}")
                finally:
                    self.browser = None
        except Exception as e:
            print(f"Error in close_browser: {e}")
        
        try:
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            print(f"Error stopping playwright: {e}")
        finally:
            self.playwright = None