from dotenv import load_dotenv
import os
import json
from pathlib import Path
import sys
from time import sleep, time
if getattr(sys, 'frozen', False):
    bin_dir = Path(sys.executable).parent
    base_path = bin_dir.parent 
    sys.path.append(str(bin_dir))
    sys.path.append(str(bin_dir / "_internal"))
else:
    base_path = Path(__file__).resolve().parent.parent.parent
    bin_dir = base_path / "src" / "scripts"
dotenv_path = base_path / ".env"
load_dotenv(dotenv_path=dotenv_path)

os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(bin_dir / "ms-playwright")
from websocket import WebSocket
from db import DB

class InvoiceExtractor:
    def __init__(self, credentials):
        self.unregistered_products = []
        self.playwright = None
        self.browser = None
        if getattr(sys, 'frozen', False):
            self.base_path = Path(sys._MEIPASS)
        else:
            script_dir = Path(__file__).resolve().parent
            self.base_path = script_dir.parent.parent
            from dotenv import load_dotenv
            load_dotenv(dotenv_path=self.base_path / '.env')

        if "PLAYWRIGHT_BROWSERS_PATH" not in os.environ:
            executable_dir = Path(sys.executable).parent if getattr(sys, 'frozen', False) else self.base_path
            os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(executable_dir / "ms-playwright")
        self.cis_name = credentials.get('CIS_NAME')
        self.cis_passwd = credentials.get('CIS_PASSWD')  
        self.database = DB()

    def extract_invoice(self, order_data, ws: WebSocket):
        print(order_data)
        if isinstance(order_data, str):
            try:
                order_data = json.loads(order_data)
                print(f"Parsed JSON string to dict")
            except json.JSONDecodeError as e:
                raise TypeError(f"order_data is a string but not valid JSON: {e}")
            
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
            self.database.update_db_brands(updated_brands)
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
                '--disable-gpu',
                '--disable-extensions',
                '--disable-component-update',
                '--no-first-run'
            ])
            
            print("Creating new page...")
            page = self.browser.new_page()
            page.set_default_timeout(10000)
            page.set_default_navigation_timeout(10000)

            print("Navigating to login page...")
            page.goto("https://live.livecis.gr/live/", wait_until="domcontentloaded")

            print("Filling login credentials...")
            page.fill('input#MainContent_txtunm', self.cis_name)
            page.fill('input#MainContent_txtPwd', self.cis_passwd)
            page.click('input[id=MainContent_Button1]')
            print("Login form submitted")

            print("Navigating to document creation page...")
            page.goto('https://live.livecis.gr/live/Document.aspx?action=N&Personaa=&tp=%d0%d9%cb%c7%d3%c5%c9%d3', wait_until="domcontentloaded")

            print("Selecting invoice type...")
            page.locator('#MainContent_TabContainer1_TabPanel1_DocType').select_option('ΠΑΡ')

            print(f"Searching for client AFM: {client_afm}...")
            page.locator('#MainContent_TabContainer1_TabPanel1_Button6').click()
            page.locator('#MainContent_GridView1').locator(f"tr:has-text('{client_afm}')").click()
            
            print("Client selected, reloading page...")
            page.reload(wait_until="domcontentloaded")

            index = 0
            print(f"Starting product entry loop. Total products: {len(products)}")

            while index < len(products):
                print(f"Processing product {index+1}/{len(products)}: {prod_codes[index]}")
                
                if index % 35 == 0 and index != 0:
                    print("Performing periodic page reload (every 35 items)...")
                    page.reload(wait_until="domcontentloaded")

                while(prod_quantities[index] == 0):
                    print(f"Skipping {prod_codes[index]} due to zero quantity")
                    index += 1
                    if index >= len(products): break

                print(f"Clicking 'Add Product' button for {prod_codes[index]}")
                page.locator('#MainContent_Button2').click()
                page.wait_for_load_state('domcontentloaded')

                print("Waiting for search dropdown visibility...")
                page.locator('#MainContent_LLinkid_I').click()

                try:
                    page.locator('#MainContent_LLinkid_DDD_PW-1').wait_for(state='visible', timeout=5000)
                except Exception as e:
                    print(f"Making products drop down visible: {e}")
                    page.evaluate("""
                        const dropdown = document.querySelector('#MainContent_LLinkid_DDD_PW-1');
                        if (dropdown) {
                            dropdown.style.display = 'block';
                            dropdown.style.visibility = 'visible';
                        }
                    """)

                    try:
                        page.locator('#MainContent_LLinkid_B-1').click()
                    except:
                        pass

                print(f"Entering code: {prod_codes[index]}")
                page.locator('#MainContent_LLinkid_I').fill(prod_codes[index])

                print("Searching dropdown for results...")
                dropdown_codes = page.locator('#MainContent_LLinkid_DDD_PW-1').get_by_text(prod_codes[index]).all()
                dropdown_prices = page.locator('#MainContent_LLinkid_DDD_L_LBI0T3').all()
                start_dropdown_searching_time = time()
                while len(dropdown_codes) == 0 and time() - start_dropdown_searching_time < 3:
                    dropdown_codes = page.locator('#MainContent_LLinkid_DDD_PW-1').get_by_text(prod_codes[index]).all()
                    dropdown_prices = page.locator('#MainContent_LLinkid_DDD_L_LBI0T3').all()

                if len(dropdown_prices) == 0 or len(dropdown_codes) == 0:
                    print(f"Product {prod_codes[index]} NOT FOUND in search (codes: {len(dropdown_codes)}, prices: {len(dropdown_prices)})")
                    page.locator('#MainContent_ImageButton1').click()
                    self.unregistered_products.append(prod_codes[index])
                    payload = {
                        "type": "extract_invoice",
                        "data": prod_codes[index],
                        "status": "skipped"
                    }
                    json_payload = json.dumps(payload, ensure_ascii=False)
                    ws.send(json_payload)
                    index += 1
                    continue
                
                print(f"Found {len(dropdown_codes)} dropdown matches. Selecting best match...")
                correct_code_string = len(prod_codes[index])
                dropdown_code_selection = None
                for i in range(len(dropdown_codes)):
                    if len(dropdown_codes[i].inner_text()) == correct_code_string:
                        dropdown_code_selection = dropdown_codes[i]
                        correct_code_string = dropdown_codes[i].inner_text()
                
                if dropdown_code_selection is None and len(dropdown_codes) > 0:
                    dropdown_code_selection = dropdown_codes[0]
                
                if dropdown_code_selection is None:
                    print(f"ERROR: No valid dropdown selection for {prod_codes[index]}")
                    index += 1
                    continue
                
                dropdown_code_selection.click()
                print("Product selected from dropdown")

                print(f"Updating price to: {prod_prices[index]}")
                price_field = page.locator('#igtxtMainContent_Lprice')
                price_field.clear()
                price_field.fill(prod_prices[index])

                print(f"Updating quantity to: {prod_quantities[index]}")
                page.locator('#igtxtMainContent_Lquant').fill(str(prod_quantities[index]))

                print("Clicking confirm (plus button)...")
                page.locator('#MainContent_ImageButton1').click()
                payload = {
                    "type": "extract_invoice",
                    "data": prod_codes[index],
                    "status": "completed"
                }
                json_payload = json.dumps(payload, ensure_ascii=False)
                ws.send(json_payload)
                index += 1

            print("All products entered. Proceeding to shipping/fees...")
            page.locator('#MainContent_BtnServ').click()

            print("Waiting for shipping dropdown...")
            page.locator('#MainContent_LLinkid0_B-1').click()

            try:
                page.locator('#MainContent_LLinkid0_DDD_PW-1').wait_for(state='visible', timeout=5000)
            except:
                page.evaluate("""
                    const dropdown = document.querySelector('#MainContent_LLinkid0_DDD_PW-1');
                    if (dropdown) {
                        dropdown.style.display = 'block';
                        dropdown.style.visibility = 'visible';
                    }
                """)
            page.locator('#MainContent_LLinkid0_DDD_L_LBI5T0').click()

            print(f"Setting shipping tax: {shipping_tax}")
            try:
                page.locator('#igtxtMainContent_Lprice0').fill(str(shipping_tax).replace('.', ','))
            except Exception as e:
                print(f"Error in locator #igtxtMainContent_Lprice0: {e}")
            
            try:
                page.locator('#igtxtMainContent_Lquant0').fill('1')
            except Exception as e:
                print(f"Error in locator #igtxtMainContent_Lquant0: {e}")
            sleep(0.1)
            try:
                page.locator('#MainContent_BtLineIN').click()
            except Exception as e:
                print(f"Error in locator #MainContent_BtLineIN: {e}")
            
            print("Finalizing document...")
            page.locator('#MainContent_Button5').click()
            sleep(1)
            page.locator('#MainContent_InButon').click()
            print("Process finished successfully")
            payload = {
                "type": "invoice_extraction_finished"
            }
            json_payload = json.dumps(payload, ensure_ascii=False)
            ws.send(json_payload)

        except Exception as e:
            print(f"CRASH in invoice extraction: {e}")
            payload = {
                "type": "invoice_extraction_error",
                "data": str(e)
            }
            json_payload = json.dumps(payload, ensure_ascii=False)
            ws.send(json_payload)
        
        finally:
            print("Cleaning up resources...")
            self.close_browser()

    def close_browser(self):
        try:
            if self.browser:
                try:
                    self.browser.close()
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