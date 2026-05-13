import os
import json
import signal
import gc  # Added for manual memory management
from contextlib import contextmanager
from .DataFetcher import update_db_brands

class TimeoutException(Exception):
    pass

@contextmanager
def timeout(seconds):
    def handler(signum, frame):
        raise TimeoutException("Operation timed out")
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
        """Helper to (re)start playwright and browser with ultra-low-memory settings"""
        from playwright.sync_api import sync_playwright
        
        # Ensure previous session is dead
        self.close_browser()
        
        self.playwright = sync_playwright().start()
        # Added --disable-dev-shm-usage and --js-flags for strict RAM limits
        self.browser = self.playwright.chromium.launch(headless=True, args=[
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage', # Uses /tmp instead of shared memory
            '--disable-gpu',
            '--single-process', # Forces everything into one process
            '--js-flags="--max-old-space-size=128 --stack-size=2048"',
            '--disable-extensions',
            '--disable-component-update',
            '--no-first-run'
        ])
        
        # Create context with a generic user agent to avoid some bloat
        context = self.browser.new_context()
        page = context.new_page()
        
        # Aggressively block heavy assets
        page.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2,ttf,css,pdf}", lambda route: route.abort())
        
        try:
            page.goto("https://live.livecis.gr/live/", wait_until="networkidle", timeout=30000)
            page.fill('input#MainContent_txtunm', self.cis_name)
            page.fill('input#MainContent_txtPwd', self.cis_passwd)
            page.click('input[id=MainContent_Button1]')
            
            page.goto('https://live.livecis.gr/live/Materials.aspx?tp=%C5%DF%E4%EF%F2', wait_until="networkidle")
            page.locator('#MainContent_Button1').click()
        except Exception as e:
            print(f"Login failed: {e}")
            raise
            
        return page

    def register(self, order_data):
        products = order_data["products"]
        updated_brands = order_data["updated_brands"]
        
        update_db_brands(updated_brands)

        try:
            page = self.start_session()

            for i, prod in enumerate(products):
                # RECYCLE BROWSER: Every 8 products to stay under 512MB
                if i % 8 == 0 and i != 0:
                    print(f"Memory Management: Recycling browser at index {i}")
                    page = self.start_session()

                if not prod.get("isRegistered", False):
                    try:
                        page.wait_for_load_state('domcontentloaded', timeout=10000)
                        page.fill('input#MainContent_Code', prod['code'])
                        page.fill('input#MainContent_Descr', prod.get('description', ''))
                        page.locator('#MainContent_TabContainer1_TabPanel1_Bmu').select_option('ΤΕΜ')
                        page.fill('input#MainContent_TabContainer1_TabPanel1_WSPPrice', str(prod['price']))
                        
                        page.locator('#MainContent_Innext').click()
                        
                        yield f"data: {json.dumps({'type': 'COMPLETE', 'code': prod['code']})}\n\n"
                    except Exception as e:
                        print(f"Error on item {prod['code']}: {e}")
                        # If a single item fails, attempt to refresh the page to clear state
                        page.goto('https://live.livecis.gr/live/Materials.aspx?tp=%C5%DF%E4%EF%F2')
            
            yield f"data: {json.dumps({'type': 'FINISHED'})}\n\n"

        except Exception as e:
            print(f"Critical error: {e}")
            yield f"data: {json.dumps({'type': 'ERROR', 'message': str(e)})}\n\n"
        finally:
            self.close_browser()

    def close_browser(self):
        """Aggressively clear memory and processes"""
        try:
            if self.browser:
                self.browser.close()
        except:
            pass
        finally:
            self.browser = None
        
        try:
            if self.playwright:
                self.playwright.stop()
        except:
            pass
        finally:
            self.playwright = None
            
        # Crucial for staying under 512MB: Force Python's GC
        gc.collect()