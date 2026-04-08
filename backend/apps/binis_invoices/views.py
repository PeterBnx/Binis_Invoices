from django.http import JsonResponse
from .DataFetcher import DataFetcher

def get_orders(request):
    data_fetcher = DataFetcher()
    data_fetcher.fetch_all_orders()
    data = []

    for order in data_fetcher.emp_orders:
        data.append({
            "id": order.id, "client": order.client, "date": order.date, "status": order.status
        })
    return JsonResponse(data, safe=False)
