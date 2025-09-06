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
def checkout_design_view(request):
    return render(request, "main/user_checkout.html")

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
    # First, check if user selected an existing address
        selected_address_id = request.POST.get("address_id")
        if selected_address_id:
            address_obj = get_object_or_404(UserAddress, id=selected_address_id, user=request.user)
        else:
            # --- Case 2: User submitted a new address ---
            fname = request.POST.get("fname")
            lname = request.POST.get("lname")
            full_name = f"{fname} {lname}".strip()  # combine into full name
            
            phone = request.POST.get("phone")
            email = request.POST.get("email")
            house = request.POST.get("house")
            street = request.POST.get("street")
            landmark = request.POST.get("landmark")
            label = request.POST.get("label", "Home")

            # Save the new address
            if full_name and phone:
                address_obj = request.user.addresses.create(
                    full_name=full_name,
                    phone=phone,
                    email=email,
                    house=house,
                    street=street,
                    landmark=landmark,
                )
                
                # ✅ Auto-select this new address
                selected_address_id = address_obj.id
            else:
                messages.error(request, "Please provide your name and phone number.")
                return redirect("orders:checkout_view")


        # Check stock availability BEFORE creating the order
        for item in cart_items:
            if item.product.stock < item.quantity:
                messages.error(
                    request,
                    f"Not enough stock for {item.product.name}. Only {item.product.stock} left."
                )
                return redirect("cart:cart_view")  # redirect user back to cart

        # Create Order
        order = Order.objects.create(
            user=request.user,
            full_name=address_obj.full_name,
            phone=address_obj.phone,
            email=address_obj.email,
            address=f"{address_obj.house}, {address_obj.street}, Dalig, Antipolo, Rizal 1870, {address_obj.landmark}",
            status="pending",
        )

        # Create OrderItem and deduct stock
        for item in cart_items:
            order.items.create(
                product=item.product,
                quantity=item.quantity,
                price_at_purchase=item.product.price,
            )
            # Deduct stock
            item.product.stock -= item.quantity
            item.product.save()

        # Remove **only the purchased items** from cart
        cart.items.filter(id__in=[i.id for i in cart_items]).delete()

        messages.success(request, "Your order has been placed successfully!")
        return redirect("orders:my_orders")

    context = {
        "cart_items": cart_items,
        "total": total,
        "addresses": request.user.addresses.all(),  # ✅ Pass addresses to template
    }
    return render(request, "main/user_checkout.html", context)



# Test for Design
from django.shortcuts import render

def orders_page(request):
    return render(request, "main/orders.html")  # this is your design-only template








