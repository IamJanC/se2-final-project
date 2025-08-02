from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.my_orders, name='my_orders'),  # User-facing orders page
    path('create/', views.create_order, name='create_order'),  # Page to create a new order
]