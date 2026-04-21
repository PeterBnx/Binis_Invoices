from django.urls import path
from . import views

urlpatterns = [
    path('binis_invoices/orders/', views.get_orders),
    path('binis_invoices/orders/<str:order_number>/', views.get_products_of_order)
]