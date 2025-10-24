from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'adminpanel'

urlpatterns = [
    path('admin/', views.dashboard_view, name='dashboard'),
    path('logout/', LogoutView.as_view(next_page='main:home'), name='logout'),
    path('delete/<int:pk>/', views.delete_product, name='delete_product'),
    path("edit/<int:pk>/", views.edit_product, name="edit_product"),
    path("export-pdf/", views.export_pdf, name="export_pdf"),

    # ✅ Fixed the duplicate "custom-dashboard"
    path("custom-dashboard/", views.dashboard_view, name="custom_dashboard"),

    # ✅ Category management
    path("categories/add/", views.create_category, name="create_category"),
    path("categories/validate/", views.validate_category, name="validate_category"),
    path("categories/delete/<int:pk>/", views.delete_category, name="delete_category"),

    # ✅ Orders
    path("orders/", views.admin_orders, name="admin_orders"),

    # ✅ Products
    path("products/", views.products_view, name="products"),
    path("category/create/", views.create_category, name="create_category"),
    path("category/delete/<int:pk>/", views.delete_category, name="delete_category"),
    path("category/validate/", views.validate_category, name="validate_category"),
]
