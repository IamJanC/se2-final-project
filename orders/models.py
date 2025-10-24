from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product
from django.conf import settings

User = get_user_model()

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    full_name = models.CharField(max_length=100)   # customer's name
    phone = models.CharField(max_length=20)        # contact number
    email = models.EmailField(blank=True)          # optional, for receipts
    address = models.TextField()                   # delivery address
    
    # Snapshot of address at checkout
    house = models.CharField(max_length=100, blank=True)
    street = models.CharField(max_length=100, blank=True)
    landmark = models.CharField(max_length=100, blank=True)
    label = models.CharField(max_length=50, default="Home")
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"
    
    def total(self):
        return sum(item.quantity * item.price_at_purchase for item in self.items.all())
    


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="order_items")
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    @property
    def subtotal(self):
        return self.quantity * self.price_at_purchase

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order {self.order.id})"
    
    
    
class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    house = models.CharField(max_length=100, blank=True)
    street = models.CharField(max_length=100, blank=True)
    landmark = models.CharField(max_length=100, blank=True)
    label = models.CharField(max_length=50, default="Home")  # e.g., Home, Work
    created_at = models.DateTimeField(auto_now_add=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} - {self.house}, {self.street}"

