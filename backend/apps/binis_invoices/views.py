from django.http import JsonResponse

def get_orders(request):
    # Example data structure matching your Order interface
    data = [
        {"id": "1", "client": "Alice", "date": "2026-04-07", "status": "Pending"},
        {"id": "2", "client": "Bob", "date": "2026-04-08", "status": "Completed"},
    ]
    return JsonResponse(data, safe=False)