from django.urls import include, path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from . import views

User = get_user_model()

# Add these view functions above your urlpatterns
def check_username(request):
    username = request.GET.get('username', '').strip()
    available = not User.objects.filter(username__iexact=username).exists()  # Case insensitive
    return JsonResponse({'available': available})

def check_email(request):
    email = request.GET.get('email', '').strip().lower()  # Convert to lowercase
    available = not User.objects.filter(email__iexact=email).exists()  # Case insensitive
    return JsonResponse({'available': available})

urlpatterns = [
    path('product-success/', views.success, name='product-success'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('', views.index, name='index'),
    
    # Authentication
    path('login', views.custom_login, name='login'),
    path("register", views.register_view, name="register"),
    
    # Add these new endpoints
    path('check_username/', views.check_username, name='check_username'),
    path('check_email/', views.check_email, name='check_email'),
]
