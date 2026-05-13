import json
import websocket
from DataFetcher import DataFetcher

def main():
    try:
        # Establish connection
        ws = websocket.create_connection('ws://localhost:5555/websocket')

        data_fetcher = DataFetcher()
        data_fetcher.fetch_all_orders()
        order_data = [order.to_dict() for order in data_fetcher.emp_orders]

        # print("[PYTHON] 2: ", [order.client for order in data_fetcher.emp_orders])

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
            print("WebSocket connection closed.")

if __name__ == "__main__":
    main()