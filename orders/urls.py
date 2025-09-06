from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.my_orders, name='my_orders'),  # User-facing orders page
    # path('create/', views.create_order, name='create_order'),  # Page to create a new order
    
    
    
    path("checkout/design/", views.checkout_design_view, name="checkout_design"), #for designing user_checkout.html
    path("checkout/", views.checkout_view, name="checkout"), #final ^ temp ^
    
    
    path("design/", views.orders_page, name="orders_design"), #for designing orders.html
]