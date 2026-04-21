from django.http import JsonResponse
from .DataFetcher import DataFetcher

def get_orders(request):
    data_fetcher = DataFetcher()
    data_fetcher.fetch_all_orders()
    data = []

    for order in data_fetcher.emp_orders:
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
            "name": product.name,
            "quantity": product.quantity,
            "price": product.price
        })
        
    return JsonResponse(products_list, safe=False)