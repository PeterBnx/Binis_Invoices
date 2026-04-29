import uuid
from django.core.cache import cache
from django.http import JsonResponse, StreamingHttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .DataFetcher import DataFetcher
from .InvoiceMaker import InvoiceMaker
from .ProductsRegister import ProductsRegister

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
        "products": products_list,
        "shippingTax": data_fetcher.shipping_tax
    }
    return JsonResponse(data, safe=False)


@api_view(['POST'])
def store_extraction_data(request):
    session_id = str(uuid.uuid4())
    # Store the products data in cache for 10 minutes
    cache.set(f"extract_{session_id}", request.data, 600)
    return Response({"session_id": session_id})

def extract_invoice(request, session_id):
    data = cache.get(f"extract_{session_id}")
    if not data:
        return StreamingHttpResponse("data: {\"error\": \"Expired\"}\n\n", content_type='text/event-stream')

    invoice_maker = InvoiceMaker()
    return StreamingHttpResponse(invoice_maker.make_invoice(data), content_type='text/event-stream')

@api_view(['POST'])
def store_register_data(request):
    session_id = str(uuid.uuid4())
    # Store the products data in cache for 10 minutes
    cache.set(f"extract_{session_id}", request.data, 600)
    return Response({"session_id": session_id})

def register_products(request, session_id):
    data = cache.get(f"extract_{session_id}")
    if not data:
        return StreamingHttpResponse("data: {\"error\": \"Expired\"}\n\n", content_type='text/event-stream')

    products_register = ProductsRegister()
    return StreamingHttpResponse(products_register.register(data), content_type='text/event-stream')