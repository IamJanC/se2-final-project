from django.shortcuts import render,get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages  # ✅ Add this
from .models import Order
from cart.models import Cart  # adjust if your cart app has a different path



@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at').prefetch_related('items__product')
    return render(request, 'main/my_orders.html', {'orders': orders})

@login_required
def checkout_view(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()
    total = sum(item.product.price * item.quantity for item in cart_items)  # ✅ inline subtotal
    for item in cart_items:
        item.subtotal = item.product.price * item.quantity
    
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        address = request.POST.get("address")

        # ✅ Create Order linked to the logged-in user
        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            email=email,
            address=address,
            status="pending",
        )

        # ✅ Create OrderItem for each cart item
        for item in cart_items:
            order.items.create(
                product=item.product,
                quantity=item.quantity,
                price_at_purchase=item.product.price,
            )

        # ✅ Clear the cart after checkout
        cart.items.all().delete()

        messages.success(request, "Your order has been placed successfully!")
        return redirect("orders:my_orders")

    context = {
        "cart_items": cart_items,
        "total": total,
    }
    return render(request, "main/checkout.html", context)
