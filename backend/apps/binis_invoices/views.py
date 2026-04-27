from django.http import JsonResponse, StreamingHttpResponse
from .DataFetcher import DataFetcher
from .InvoiceMaker import InvoiceMaker

def get_orders(request):
    orders_data_fetcher = DataFetcher()
    orders_data_fetcher.fetch_all_orders()
    data = []

    for order in orders_data_fetcher.emp_orders:
        data.append({
            "id": order.id, "client": order.client, "date": order.date, "price": order.price
        })
    return JsonResponse(data, safe=False)

def get_products_of_order(request, order_number):
    data_fetcher = DataFetcher()
    data_fetcher.fetch_order_products_data(order_number)
    products_list = []
    for product in data_fetcher.order_products:
        products_list.append({
            "quantity": product.quantity,
            "code": product.code,
            "description": product.description,
            "price": product.price,
            "isRegistered": product.is_registered,
            "brandFull": product.brand_full,
            "brandShort": product.brand_short
        })
    data = {
        "orderNumber": order_number,
        "clientName": data_fetcher.client_name,
        "clientVAT": data_fetcher.client_afm,
        "products": products_list 
    }
    return JsonResponse(data, safe=False)

def extract_invoice(request, order_number):
    invoice_maker = InvoiceMaker()
    data_fetcher = DataFetcher()
    data_fetcher.fetch_order_products_data(order_number)
    invoice_maker.make_invoice(data_fetcher, 'tda')
    return StreamingHttpResponse(invoice_maker.make_invoice(data_fetcher, 'tda'), content_type='text/event-stream')