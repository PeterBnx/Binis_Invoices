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
        print(f"Starting make_invoice for client AFM: {order_data.get('client_afm')}")
        products = order_data["products"]
        client_afm = order_data["client_afm"]
        shipping_tax = order_data["shipping_tax"]
        updated_brands = order_data["updated_brands"]
        prod_codes = [prod['code'] for prod in products]
        prod_quantities = [prod['quantity'] for prod in products]
        prod_prices = [prod['price'] for prod in products]
        
        try:
            print("Attempting to update DB brands...")
            update_db_brands(updated_brands)
            print("DB brands updated successfully")
        except Exception as e:
            print(f"Failed to update DB brands: {e}")

        try:
            from playwright.sync_api import sync_playwright
            print("Starting Playwright...")
            self.playwright = sync_playwright().start()
            print("Launching Chromium...")
            self.browser = self.playwright.chromium.launch(headless=True, args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--single-process'
            ])
            
            print("Creating new page...")
            page = self.browser.new_page()
            page.set_default_timeout(15000)
            page.set_default_navigation_timeout(15000)
            
            print("Navigating to login page...")
            page.goto("https://live.livecis.gr/live/")

            print("Filling login credentials...")
            page.fill('input#MainContent_txtunm', self.cis_name)
            page.fill('input#MainContent_txtPwd', self.cis_passwd)
            page.click('input[id=MainContent_Button1]')
            print("Login form submitted")

            print("Navigating to document creation page...")
            page.goto('https://live.livecis.gr/live/Document.aspx?action=N&Personaa=&tp=%d0%d9%cb%c7%d3%c5%c9%d3')

            print("Selecting invoice type...")
            page.locator('#MainContent_TabContainer1_TabPanel1_DocType').select_option('ΠΑΡ')

            print(f"Searching for client AFM: {client_afm}...")
            page.locator('#MainContent_TabContainer1_TabPanel1_Button6').click()
            page.locator('#MainContent_GridView1').locator(f"tr:has-text('{client_afm}')").click()
            
            print("Client selected, reloading page...")
            page.reload()

            index = 0
            print(f"Starting product entry loop. Total products: {len(products)}")
            while index < len(products):
                print(f"Processing product {index+1}/{len(products)}: {prod_codes[index]}")
                
                if index % 35 == 0 and index != 0:
                    print("Performing periodic page reload (every 35 items)...")
                    page.reload()

                while(prod_quantities[index] == 0):
                    print(f"Skipping {prod_codes[index]} due to zero quantity")
                    index += 1
                    if index >= len(products): break

                print(f"Clicking 'Add Product' button for {prod_codes[index]}")
                page.locator('#MainContent_Button2').click()

                print("Waiting for search dropdown visibility...")
                while not page.locator('#MainContent_LLinkid_DDD_PW-1').is_visible():
                    page.locator('#MainContent_LLinkid_I').click()

                print(f"Entering code: {prod_codes[index]}")
                page.locator('#MainContent_LLinkid_I').fill(prod_codes[index])

                print("Searching dropdown for results...")
                dropdown_codes = page.locator('#MainContent_LLinkid_DDD_PW-1').get_by_text(prod_codes[index]).all()
                dropdown_prices = page.locator('#MainContent_LLinkid_DDD_L_LBI0T3').all()

                start_dropdown_searching_time = time()
                while len(dropdown_codes) == 0 and time() - start_dropdown_searching_time < 3:
                    dropdown_codes = page.locator('#MainContent_LLinkid_DDD_PW-1').get_by_text(prod_codes[index]).all()
                    dropdown_prices = page.locator('#MainContent_LLinkid_DDD_L_LBI0T3').all()

                if len(dropdown_prices) == 0:
                    print(f"Product {prod_codes[index]} NOT FOUND in search")
                    page.locator('#MainContent_ImageButton1').click()
                    self.unregistered_products.append(prod_codes[index])
                    yield f"data: {json.dumps({'type': 'SKIPPED', 'code': prod_codes[index]})}\n\n"
                    index += 1
                    continue
                
                print(f"Found {len(dropdown_codes)} dropdown matches. Selecting best match...")
                correct_code_string = len(prod_codes[index])
                dropdown_code_selection = prod_codes[index]
                dropdown_price_selection = prod_prices[index]
                for i in range(len(dropdown_codes)):
                    if len(dropdown_codes[i].inner_text()) == correct_code_string:
                        dropdown_code_selection = dropdown_codes[i]
                        correct_code_string = dropdown_codes[i].inner_text()
                        dropdown_price_selection = dropdown_prices[i].inner_text()
                
                dropdown_code_selection.click()
                print("Product selected from dropdown")

                print(f"Updating price to: {prod_prices[index]}")
                if dropdown_price_selection == '0.00':
                    sleep(2)
                    page.locator('#igtxtMainContent_Lprice').clear()
                    page.locator('#igtxtMainContent_Lprice').fill(prod_prices[index])
                else:
                    while page.locator('#igtxtMainContent_Lprice').get_attribute('value') == '0,00':
                        pass
                    page.locator('#igtxtMainContent_Lprice').clear()
                    page.locator('#igtxtMainContent_Lprice').fill(prod_prices[index])

                print(f"Updating quantity to: {prod_quantities[index]}")
                page.locator('#igtxtMainContent_Lquant').fill(str(prod_quantities[index]))

                print("Clicking confirm (plus button)...")
                page.locator('#MainContent_ImageButton1').click()
                
                yield f"data: {json.dumps({'type': 'COMPLETE', 'code': prod_codes[index]})}\n\n"
                index += 1

            print("All products entered. Proceeding to shipping/fees...")
            page.locator('#MainContent_BtnServ').click()

            print("Waiting for shipping dropdown...")
            while not page.locator('#MainContent_LLinkid0_DDD_PW-1').is_visible():
                page.locator('#MainContent_LLinkid0_B-1').click()
            page.locator('#MainContent_LLinkid0_DDD_L_LBI5T0').click()
            sleep(1)

            print(f"Setting shipping tax: {shipping_tax}")
            page.locator('#igtxtMainContent_Lprice0').fill(str(shipping_tax).replace('.', ','))
            page.locator('#igtxtMainContent_Lquant0').fill('1')
            page.locator('#MainContent_BtLineIN').click()
            
            print("Finalizing document...")
            sleep(1)
            page.locator('#MainContent_Button5').click()
            sleep(1)
            page.locator('#MainContent_InButon').click()
            sleep(1)
            
            print("Taking final screenshot...")
            page.screenshot(path="/app/shared_data/invoice.png", full_page=True)
            print("Process finished successfully")
            yield f"data: {json.dumps({'type': 'FINISHED'})}\n\n"

        except Exception as e:
            print(f"CRASH in make_invoice: {e}")
            yield f"data: {json.dumps({'type': 'ERROR', 'message': str(e)})}\n\n"
        
        finally:
            print("Cleaning up resources...")
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