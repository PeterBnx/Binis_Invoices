import uuid
from django.core.cache import cache
from django.http import HttpResponseForbidden, JsonResponse, StreamingHttpResponse
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
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

def add_cors_headers(response, request):
    """
    Add CORS headers to a response for cross-origin requests.
    """
    origin = request.META.get('HTTP_ORIGIN')
    if origin:
        response['Access-Control-Allow-Origin'] = origin
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'accept, authorization, content-type, user-agent, x-csrftoken, x-requested-with'
    return response

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
@permission_classes([AllowAny])
def extract_invoice(request, session_id):
    token_key = get_token_from_request(request)
    if not token_key or not Token.objects.filter(key=token_key).exists():
        return HttpResponseForbidden("Invalid Token")
    
    data = cache.get(f"extract_{session_id}")
    if not data:
        response = StreamingHttpResponse("data: {\"error\": \"Expired\"}\n\n", content_type='text/event-stream')
        return add_cors_headers(response, request)

    invoice_maker = InvoiceMaker()
    response = StreamingHttpResponse(invoice_maker.make_invoice(data), content_type='text/event-stream')
    return add_cors_headers(response, request)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def store_register_data(request):
    session_id = str(uuid.uuid4())
    cache.set(f"register_{session_id}", request.data, 600)
    return Response({"session_id": session_id})

@api_view(['GET'])
@permission_classes([AllowAny])
def register_products(request, session_id):
    token_key = get_token_from_request(request)
    if not token_key or not Token.objects.filter(key=token_key).exists():
        return HttpResponseForbidden("Invalid Token")

    data = cache.get(f"register_{session_id}")
    if not data:
        response = StreamingHttpResponse("data: {\"error\": \"Expired\"}\n\n", content_type='text/event-stream')
        return add_cors_headers(response, request)

    products_register = ProductsRegister()
    response = StreamingHttpResponse(products_register.register(data), content_type='text/event-stream')
    return add_cors_headers(response, request)

@api_view(['POST', 'OPTIONS'])
@permission_classes([AllowAny])
def login_view(request):
    if request.method == 'OPTIONS':
        return Response(status=200)
    
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({'error': 'Username and password are required'}, status=400)
    
    user = authenticate(username=username, password=password)
    
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})
    return Response({'error': 'Λανθασμένα στοιχεία σύνδεσης'}, status=400)