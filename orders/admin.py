from django.contrib import admin
from .models import Order, OrderItem, UserAddress


class OrderItemInline(admin.TabularInline):  # lets you edit items inside an Order
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "full_name", "status", "created_at", "total_display")
    list_filter = ("status", "created_at")
    search_fields = ("full_name", "phone", "email", "user__username")
    inlines = [OrderItemInline]

    def total_display(self, obj):
        return obj.total()
    total_display.short_description = "Total"


@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "full_name", "phone", "email", "house", "street", "landmark", "created_at")
    search_fields = ("full_name", "phone", "email", "user__username")
    list_filter = ("created_at",)


# Optional: Register OrderItem separately if you want direct access
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product", "quantity", "price_at_purchase", "subtotal")
    search_fields = ("order__id", "product__name")
    list_filter = ("order__created_at",)
