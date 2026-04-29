from django.urls import path
from . import views

urlpatterns = [
    path('binis_invoices/orders/', views.get_orders),
    path('binis_invoices/orders/<str:order_number>/', views.get_products_of_order),
    path('binis_invoices/extract_invoice/<str:session_id>', views.extract_invoice),
    path('binis_invoices/store_extraction_data', views.store_extraction_data),
    path('binis_invoices/register_products/<str:session_id>', views.register_products),
    path('binis_invoices/store_register_data', views.store_register_data),
]