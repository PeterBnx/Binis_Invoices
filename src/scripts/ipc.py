import json
import websocket
from DataFetcher import DataFetcher
import sys

def main():
    try:
        # Establish connection
        ws = websocket.create_connection('ws://localhost:5555/websocket')
        
        print(sys.argv[1])
        data_fetcher = DataFetcher()
        if (len(sys.argv[1]) > 0):
            data_fetcher.fetch_order_products_data(sys.argv[1])
            order_products = [product.to_dict() for product in data_fetcher.order_products]
            data = {
                "products": order_products,
                "client_name": str(data_fetcher.client_name),
                "client_afm": str(data_fetcher.client_afm),
                "shipping_tax": str(data_fetcher.shipping_tax),
                "order_number": sys.argv[1]
            }
            print(data)
            payload = {
                "type": "order_data",
                "data": data
            }
        else:
            data_fetcher.fetch_all_orders()
            order_data = [order.to_dict() for order in data_fetcher.emp_orders]
            payload = {
                "type": "emp_orders",
                "data": order_data
            }
        json_payload = json.dumps(payload, ensure_ascii=False)
        ws.send(json_payload)

    except Exception as e:
        print(f"Connection or transmission error: {e}")
    
    finally:
        if 'ws' in locals():
            ws.close()

if __name__ == "__main__":
    main()