from django.urls import path
from . import views

urlpatterns = [
    path('binis_invoices/orders/', views.get_orders)
]