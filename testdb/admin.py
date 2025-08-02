from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class ProductsAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock')

admin.site.register(CustomUser, UserAdmin)

