from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .models import Products

admin.site.register(Products)
admin.site.register(CustomUser, UserAdmin)
