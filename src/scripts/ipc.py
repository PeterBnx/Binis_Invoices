import json
import os
import sys
from pathlib import Path
import websocket
from db import DB

if getattr(sys, 'frozen', False):
    bin_dir = Path(sys.executable).parent
    base_path = bin_dir.parent.parent
    sys.path.append(str(bin_dir))
    sys.path.append(str(bin_dir / "_internal"))
else:
    base_path = Path(__file__).resolve().parent.parent.parent
    bin_dir = base_path / "src" / "scripts"

os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(bin_dir / "ms-playwright")

from data_fetcher import DataFetcher
from products_registor import ProductsRegister
from invoice_extractor import InvoiceExtractor

credentials = {
    "EMP_NAME": None,
    "EMP_PASSWD": None,
    "CIS_NAME": None,
    "CIS_PASSWD": None
}
db = DB()

def load_credentials_from_db():
    try:
        if db.check_creds():
            credentials['EMP_NAME'] = db.credentials[0]
            credentials['EMP_PASSWD'] = db.credentials[1]
            credentials['CIS_NAME'] = db.credentials[2]
            credentials['CIS_PASSWD'] = db.credentials[3]
            print("Credentials loaded successfully.",  credentials)
            return True
        return False
    except Exception as e:
        print(f"ERROR reading credentials: {e}")
        return False

def main():
    payload = {}
    try:
        ws = websocket.create_connection('ws://localhost:5555/websocket')

        if (sys.argv[1] == "save_credentials"):
            print("Hello from creds")
            success = db.update_creds(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
            payload = {
                "type": "credentials_saved",
                "status": success
            }
            json_payload = json.dumps(payload, ensure_ascii=False)
            ws.send(json_payload)
            return
        
        if not load_credentials_from_db():
            payload = {
                "type": "empty_credentials"
            }
            json_payload = json.dumps(payload, ensure_ascii=False)
            ws.send(json_payload)
            return
        
        dataFetcher = DataFetcher(credentials)

        if sys.argv[1] == "get_orders":
            dataFetcher.fetch_all_orders()
            order_data = [order.to_dict() for order in dataFetcher.emp_orders]
            payload = {
                "type": "emp_orders",
                "data": order_data
            }
        elif (sys.argv[1] == "get_order_data"):
            dataFetcher.fetch_order_products_data(sys.argv[2])
            order_products = [product.to_dict() for product in dataFetcher.order_products]
            data = {
                "products": order_products,
                "client_name": str(dataFetcher.client_name),
                "client_afm": str(dataFetcher.client_afm),
                "shipping_tax": str(dataFetcher.shipping_tax),
                "order_number": sys.argv[2]
            }
            payload = {
                "type": "order_data",
                "data": data
            }
        elif (sys.argv[1] == "register_products"):
            try:
                input_data = sys.stdin.read()
                data = json.loads(input_data)
                products_register = ProductsRegister(data, ws, credentials)
                payload = {"type": "register_initiated"}
            except Exception as e:
                print(f"Register error: {e}")
                payload = {"type": "error", "message": str(e)}
        elif (sys.argv[1] == "extract_invoice"):
            try:
                input_data = sys.stdin.read()
                data = json.loads(input_data)
                invoiceExtractor = InvoiceExtractor(credentials)
                invoiceExtractor.extract_invoice(data, ws)
                payload = {"type": "invoice_extraction_initiated"}
            except Exception as e:
                print(f"Extract invoice error: {e}")
                payload = {"type": "error", "message": str(e)}
        json_payload = json.dumps(payload, ensure_ascii=False)
        ws.send(json_payload)

    except Exception as e:
        print(f"Connection or transmission error: {e}")
    
    finally:
        if 'ws' in locals():
            ws.close()

if __name__ == "__main__":
    main()