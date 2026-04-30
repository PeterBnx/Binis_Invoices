import os
from time import sleep
import json
import signal
from contextlib import contextmanager
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
        signal.alarm(0)

class ProductsRegister:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.cis_name = os.environ.get('CIS_NAME')
        self.cis_passwd = os.environ.get('CIS_PASSWD')

    def start_session(self):
        """Helper to (re)start playwright and browser with low-memory settings"""
        from playwright.sync_api import sync_playwright
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True, args=[
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--single-process',
            '--js-flags="--max-old-space-size=128"',
            '--disable-extensions'
        ])
        page = self.browser.new_page()
        
        # Aggressively block images and fonts to save RAM
        page.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2,ttf}", lambda route: route.abort())
        
        # Login
        page.goto("https://live.livecis.gr/live/")
        page.fill('input#MainContent_txtunm', self.cis_name)
        page.fill('input#MainContent_txtPwd', self.cis_passwd)
        page.click('input[id=MainContent_Button1]')
        
        # Navigate to materials
        page.goto('https://live.livecis.gr/live/Materials.aspx?tp=%C5%DF%E4%EF%F2')
        page.locator('#MainContent_Button1').click()
        return page

    def register(self, order_data):
        products = order_data["products"]
        updated_brands = order_data["updated_brands"]
        prod_codes = [prod['code'] for prod in products]
        prod_is_registered = [prod["isRegistered"] for prod in products]
        prod_prices = [prod['price'] for prod in products]
        prod_descriptions = [prod["description"] for prod in products]

        update_db_brands(updated_brands)

        try:
            page = self.start_session()

            for i in range(len(prod_codes)):
                # RECYCLE BROWSER: Every 15 products, close and reopen to purge RAM
                if i % 15 == 0 and i != 0:
                    print(f"Memory Check: Recycling browser session at index {i}")
                    self.close_browser()
                    page = self.start_session()

                if (not prod_is_registered[i]):
                    page.wait_for_load_state('load')
                    page.fill('input#MainContent_Code', prod_codes[i])
                    page.fill('input#MainContent_Descr', prod_descriptions[i])
                    page.locator('#MainContent_TabContainer1_TabPanel1_Bmu').select_option('ΤΕΜ')
                    page.fill('input#MainContent_TabContainer1_TabPanel1_WSPPrice', prod_prices[i])
                    
                    # Register
                    page.locator('#MainContent_Innext').click()
                    
                    yield f"data: {json.dumps({'type': 'COMPLETE', 'code': prod_codes[i]})}\n\n"
            
            yield f"data: {json.dumps({'type': 'FINISHED'})}\n\n"

        except Exception as e:
            print(f"Error during registration: {e}")
            yield f"data: {json.dumps({'type': 'ERROR', 'message': str(e)})}\n\n"
        finally:
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