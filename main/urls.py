from django.urls import path                    # type: ignore
from . import views
from products import views as product_views
from main import views as main_views

app_name = 'main'  # ✅ Helps with reverse lookup la

urlpatterns = [
    path('', views.home, name='home'), # <- to home
    path('shop/', views.shop, name='shop'),
    path('shop/<int:product_id>/', views.product_detail, name='product_detail'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('product/', views.product, name='product'), # <- ?? check later
    
    #product and cart api
    path('api/products/<int:product_id>/', product_views.product_detail_json, name='api_product_detail'),
]
