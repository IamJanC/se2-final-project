from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .models import Products

class ProductsAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock')

admin.site.register(Products, ProductsAdmin)
admin.site.register(CustomUser, UserAdmin)

