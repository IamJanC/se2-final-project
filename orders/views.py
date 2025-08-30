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

    # Grab selected items from query params
    selected_items_ids = request.GET.get('items')
    if selected_items_ids:
        ids_list = [int(i) for i in selected_items_ids.split(',') if i.isdigit()]
        cart_items = cart.items.filter(id__in=ids_list)
    else:
        cart_items = cart.items.none()  # No items selected

    # Calculate total
    total = sum(item.product.price * item.quantity for item in cart_items)
    for item in cart_items:
        item.subtotal = item.product.price * item.quantity

    if request.method == "POST":
        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        address = request.POST.get("address")

        # Create Order
        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            email=email,
            address=address,
            status="pending",
        )

        # Create OrderItem only for selected cart items
        for item in cart_items:
            order.items.create(
                product=item.product,
                quantity=item.quantity,
                price_at_purchase=item.product.price,
            )

        # Remove **only the purchased items** from cart
        cart.items.filter(id__in=[i.id for i in cart_items]).delete()

        messages.success(request, "Your order has been placed successfully!")
        return redirect("orders:my_orders")

    context = {
        "cart_items": cart_items,
        "total": total,
    }
    return render(request, "main/checkout.html", context)



