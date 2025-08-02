from django.contrib import admin
from .models import Product, Category  # import your models

admin.site.register(Category)
admin.site.register(Product)