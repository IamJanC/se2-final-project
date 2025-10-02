from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_view, name='cart'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('add/', views.add_to_cart_api, name='api_add_to_cart'),
    path('update-item/', views.update_cart_item, name='update_cart_item'),  # <-- new
    path('delete/', views.delete_cart_item, name='delete_cart_item'),
]
