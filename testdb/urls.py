from django.urls import include, path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('add-product/', views.add_product, name='add-product'),
    path('product-success/', views.success, name='product-success'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('', views.index, name='index'),
    
    
    #login
    path('login', views.custom_login, name='login'),
    path("register", register_view, name="register"),  # Add this
]

