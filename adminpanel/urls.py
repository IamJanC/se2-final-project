from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'adminpanel'

urlpatterns = [
    path('admin/', views.dashboard, name='dashboard'),
    path('logout/', LogoutView.as_view(next_page='main:home'), name='logout'),
]
