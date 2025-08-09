from django.urls import path
from . import views

urlpatterns = [
    path('submit-complaint/', views.submit_complaint, name='submit_complaint'),
]
