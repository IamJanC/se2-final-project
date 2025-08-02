from django.urls import path                    # type: ignore
from . import views

app_name = 'main'  # ✅ Helps with reverse lookup la

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),  # <- new route
    path('product/', views.product, name='product'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    
]
