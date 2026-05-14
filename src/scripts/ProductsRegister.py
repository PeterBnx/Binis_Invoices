import os
import json
import signal
from contextlib import contextmanager
from websocket import WebSocket
from DB import DB

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
    def __init__(self, data, ws:WebSocket):
        self.playwright = None
        self.browser = None
        self.data = data
        self.ws = ws
        self.cis_name = os.environ.get('CIS_NAME')
        self.cis_passwd = os.environ.get('CIS_PASSWD')
        self.run()

    def start_session(self):
        """Start playwright and browser for faster page loads"""
        from playwright.sync_api import sync_playwright
        
        self.close_browser()
        
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False, args=[
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-gpu',
            '--disable-extensions',
            '--disable-component-update',
            '--no-first-run'
        ])

        context = self.browser.new_context()
        page = context.new_page()
        
        try:
            page.goto("https://live.livecis.gr/live/", wait_until="domcontentloaded", timeout=30000)
            page.fill('input#MainContent_txtunm', self.cis_name)
            page.fill('input#MainContent_txtPwd', self.cis_passwd)
            page.click('input[id=MainContent_Button1]')
            
            page.goto('https://live.livecis.gr/live/Materials.aspx?tp=%C5%DF%E4%EF%F2', wait_until="domcontentloaded")
            page.locator('#MainContent_Button1').click()

        except Exception as e:
            print(f"Login failed: {e}")
            raise
            
        return page

    def run(self):
        """Explicitly execute the register function"""
        try:
            self.register(self.data, self.ws)
        except Exception as e:
            print(f"ProductsRegister error: {e}")
            raise

    def register(self, order_data, ws: WebSocket):
        if isinstance(order_data, str):
            try:
                order_data = json.loads(order_data)
                print(f"Parsed JSON string to dict")
            except json.JSONDecodeError as e:
                raise TypeError(f"order_data is a string but not valid JSON: {e}")
        
        if not isinstance(order_data, dict):
            raise TypeError(f"order_data must be a dict or JSON string, got {type(order_data).__name__}")
        
        if "products" not in order_data:
            raise KeyError("order_data missing 'products' key. Keys: " + str(order_data.keys()))
        if "updated_brands" not in order_data:
            raise KeyError("order_data missing 'updated_brands' key. Keys: " + str(order_data.keys()))
        
        db = DB()
        products = order_data["products"]
        updated_brands = order_data["updated_brands"]
        
        db.update_db_brands(updated_brands)

        try:
            page = self.start_session()

            for i, prod in enumerate(products):
                if not prod.get("isRegistered", False):
                    try:
                        page.wait_for_load_state('domcontentloaded')

                        page.fill('input#MainContent_Code', prod['code'])
                        page.fill('input#MainContent_Descr', prod.get('description', ''))
                        page.locator('#MainContent_TabContainer1_TabPanel1_Bmu').select_option('ΤΕΜ')
                        page.fill('input#MainContent_TabContainer1_TabPanel1_WSPPrice', str(prod['price']))
                        
                        page.locator('#MainContent_Innext').click()
                        payload = {
                            "type": "register_products",
                            "data": prod['code'],
                            "status": "completed"
                        }
                        json_payload = json.dumps(payload, ensure_ascii=False)
                        ws.send(json_payload)
                    except Exception as e:
                        print(f"Error on item {prod['code']}: {e}")
                        payload = {
                            "type": "register_products",
                            "data": prod['code'],
                            "status": "skipped"
                        }
                        json_payload = json.dumps(payload, ensure_ascii=False)
                        ws.send(json_payload)
                        page.reload(wait_until="domcontentloaded")

            payload = {
                "type": "registering_finished",
            }
            json_payload = json.dumps(payload, ensure_ascii=False)
            ws.send(json_payload)

        except Exception as e:
            print(f"Critical error: {e}")
        finally:
            self.close_browser()

    def close_browser(self):
        """Close browser and playwright"""
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