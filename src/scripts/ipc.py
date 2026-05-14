import json
import websocket
from DataFetcher import DataFetcher
from ProductsRegister import ProductsRegister
from InvoiceExtractor import InvoiceExtractor
import sys

def main():
    payload = {}  # Always initialize payload first
    try:
        # Establish connection
        ws = websocket.create_connection('ws://localhost:5555/websocket')
        data_fetcher = DataFetcher()
        if sys.argv[1] == "get_orders":
            data_fetcher.fetch_all_orders()
            order_data = [order.to_dict() for order in data_fetcher.emp_orders]
            payload = {
                "type": "emp_orders",
                "data": order_data
            }
        elif (sys.argv[1] == "get_order_data"):
            data_fetcher.fetch_order_products_data(sys.argv[2])
            order_products = [product.to_dict() for product in data_fetcher.order_products]
            data = {
                "products": order_products,
                "client_name": str(data_fetcher.client_name),
                "client_afm": str(data_fetcher.client_afm),
                "shipping_tax": str(data_fetcher.shipping_tax),
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
                products_register = ProductsRegister(data, ws)
                payload = {"type": "register_initiated"}
            except Exception as e:
                print(f"Register error: {e}")
                payload = {"type": "error", "message": str(e)}
        elif (sys.argv[1] == "extract_invoice"):
            try:
                input_data = sys.stdin.read()
                data = json.loads(input_data)
                invoice_extractor = InvoiceExtractor()
                invoice_extractor.extract_invoice(data, ws)
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