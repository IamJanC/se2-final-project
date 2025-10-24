from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.my_orders, name='my_orders'),  # User-facing orders page
    # path('create/', views.create_order, name='create_order'),  # Page to create a new order
    
    
    
    path("checkout/design/", views.checkout_design_view, name="checkout_design"), #for designing user_checkout.html
    path("checkout/", views.checkout_view, name="checkout"), #final ^ temp ^
    path("save-address/", views.save_address, name="save_address"), # Saving a new address or editing an existing one
    
    path("design/", views.orders_page, name="orders_design"), #for designing orders.html
    
    path("delete-address/<int:address_id>/", views.delete_address, name="delete_address"), # Deleting an address
    
    path("orders/<int:order_id>/received/", views.order_received, name="order_received"), # Marking an order as received
    path("orders/<int:order_id>/return/", views.request_return, name="request_return"), # Requesting a return for an order
    path("orders/<int:order_id>/cancel/", views.cancel_order, name="cancel_order"), # Cancelling an order
    path('orders/<int:order_id>/', views.order_monitoring, name='order_monitoring'),
    
    path("set_selected_address/", views.set_selected_address, name="set_selected_address"),
    path('set-default/<int:address_id>/', views.set_default_address, name='set_default_address'),  # Set default address
    
    
    # path("order_monitoring/", views.order_monitoring, name="order_monitoring"), # to order_monitoring page
]