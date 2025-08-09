from django.urls import path                    # type: ignore
from . import views

app_name = 'main'  # ✅ Helps with reverse lookup la

urlpatterns = [
    path('', views.home, name='home'), # <- to home
    path('shop/', views.shop, name='shop'),
    path('shop/<int:product_id>/', views.product_detail, name='product_detail'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('product/', views.product, name='product'), # <- ?? check later
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'), # >- ?? check later we don't have add to cart yet
    
]
