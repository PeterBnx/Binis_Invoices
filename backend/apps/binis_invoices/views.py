import uuid
from django.core.cache import cache
from django.http import HttpResponseForbidden, JsonResponse, StreamingHttpResponse
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.renderers import StaticHTMLRenderer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .DataFetcher import DataFetcher
from .InvoiceMaker import InvoiceMaker
from .ProductsRegister import ProductsRegister

def get_token_from_request(request):
    """
    Helper to extract token from either the Authorization header 
    or the 'token' query parameter (for EventSource).
    """
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Token '):
        return auth_header.split(' ')[1]
    return request.GET.get('token')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_orders(request):
    orders_data_fetcher = DataFetcher()
    orders_data_fetcher.fetch_all_orders()
    data = []

    for order in orders_data_fetcher.emp_orders:
        data.append({
            "id": order.id, "client": order.client, "date": order.date, "price": order.price
        })
    return JsonResponse(data, safe=False)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
def store_extraction_data(request):
    session_id = str(uuid.uuid4())
    cache.set(f"extract_{session_id}", request.data, 600)
    return Response({"session_id": session_id})

@api_view(['GET'])
@renderer_classes([StaticHTMLRenderer])
@permission_classes([AllowAny])
def extract_invoice(request, session_id):
    token_key = get_token_from_request(request)
    if not token_key or not Token.objects.filter(key=token_key).exists():
        return HttpResponseForbidden("Invalid Token")
    
    data = cache.get(f"extract_{session_id}")
    if not data:
        return StreamingHttpResponse("data: {\"error\": \"Expired\"}\n\n", content_type='text/event-stream')

    invoice_maker = InvoiceMaker()
    return StreamingHttpResponse(invoice_maker.make_invoice(data), content_type='text/event-stream')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def store_register_data(request):
    session_id = str(uuid.uuid4())
    cache.set(f"register_{session_id}", request.data, 600)
    return Response({"session_id": session_id})

@api_view(['GET'])
@renderer_classes([StaticHTMLRenderer])
@permission_classes([AllowAny])
def register_products(request, session_id):
    token_key = get_token_from_request(request)
    if not token_key or not Token.objects.filter(key=token_key).exists():
        return HttpResponseForbidden("Invalid Token")

    data = cache.get(f"register_{session_id}")
    if not data:
        return StreamingHttpResponse("data: {\"error\": \"Expired\"}\n\n", content_type='text/event-stream')

    products_register = ProductsRegister()
    return StreamingHttpResponse(products_register.register(data), content_type='text/event-stream')

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})
    return Response({'error': 'Λανθασμένα στοιχεία σύνδεσης'}, status=400)