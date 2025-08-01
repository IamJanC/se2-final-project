from django.urls import include, path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from . import views
from django.urls import path
from .views import register_view, login_view, home_view

User = get_user_model()

# Ajax validation endpoints
def check_username(request):
    username = request.GET.get('username', '').strip()
    available = not User.objects.filter(username__iexact=username).exists()
    return JsonResponse({'available': available})

def check_email(request):
    email = request.GET.get('email', '').strip().lower()
    available = not User.objects.filter(email__iexact=email).exists()
    return JsonResponse({'available': available})

urlpatterns = [
    path('product-success/', views.success, name='product-success'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('', views.index, name='index'),

    # Authentication
    path('login', login_view, name='login'),
    path('register', register_view, name='register'),

    # Ajax validation
    path('check_username/', check_username, name='check_username'),
    path('check_email/', check_email, name='check_email'),

    # Home page
    path('home/', home_view, name='home'),
]
