from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'adminpanel'

urlpatterns = [
    path('admin/', views.dashboard, name='dashboard'),
    path('logout/', LogoutView.as_view(next_page='main:home'), name='logout'),
    path('delete/<int:pk>/', views.delete_product, name='delete_product'),
    path("edit/<int:pk>/", views.edit_product, name="edit_product"),
    path("export-pdf/", views.export_pdf, name="export_pdf"),
    path("custom-dashboard/", views.custom_admin_dashboard, name="custom_dashboard"),  # new one
    path("categories/add/", views.create_category, name="create_category"), #for adding new category
     path("categories/validate/", views.validate_category, name="validate_category"),  # ✅ for validating category

]
