"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin            # type: ignore
from django.urls import path, include       # type: ignore
from testdb import views as testdb_views    # 👈 import your login_view
from django.contrib.auth import views as auth_views  # 🔐 built-in authentication views
from products import views as product_views  # 👈 make sure this is still imported
from main import views as main_views # main


#Temporary
from django.shortcuts import render


urlpatterns = [
    path('admin/', admin.site.urls),  # 👈 admin panel
    path('', include('main.urls')),   # 👈 main app routing
   path('login/', auth_views.LoginView.as_view(), name='login'),  # 👈 login
    path('register', testdb_views.register_view, name='register'),  # 👈 register
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),  # 👈 logout
    path('orders/', include('orders.urls')),            # 👈 orders app
    path('products/', include('products.urls')),  # 👈 for products
    path('chatbot/', include('chatbot.urls')),   #chatbot
    path('cart/', include('cart.urls')), #cart
    path('adminpanel/', include('adminpanel.urls')),  # Custom admin dashboard
    
    # existing paths...
    path("cart/design/", lambda request: render(request, "main/user_cart.html"), name="user_cart_design"),
    path("testdb/", include("testdb.urls")),  # Or just "" if you want root-level URLs
]
