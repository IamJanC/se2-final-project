from django.shortcuts import render,get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages  # ✅ Add this
from .models import Order
from .models import UserAddress
from cart.models import Cart  # adjust if your cart app has a different path
from decimal import Decimal





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
        request.session['selected_items_ids'] = ids_list
    else:
        ids_list = request.session.get('selected_items_ids', [])
        
    
    # ✅ Always define cart_items
    cart_items = cart.items.filter(id__in=ids_list) if ids_list else cart.items.none()


    # 🧮 Calculate totals
    items_total = sum(item.product.price * item.quantity for item in cart_items)
    shop_discount = items_total * Decimal("0.20")  # 20% discount
    subtotal = items_total - shop_discount
    shipping_fee = Decimal("100.00") if cart_items else Decimal("0.00")
    final_total = subtotal + shipping_fee
    
    for item in cart_items:
        item.subtotal = item.product.price * item.quantity

    # --- NEW: track selected address
    selected_address_id = request.session.get("selected_address_id")
    if selected_address_id:
        default_address = request.user.addresses.filter(id=selected_address_id).first()
    else:
        # fallback to the first address if none selected
        default_address = request.user.addresses.first()

    if request.method == "POST":

        # Place Order
        if "place_order" in request.POST:
            selected_address_id = request.POST.get("address_id") or request.session.get("selected_address_id")
            if not selected_address_id:
                messages.error(request, "Please select an address before placing an order.")
                return redirect("orders:checkout")

            address_obj = get_object_or_404(UserAddress, id=selected_address_id, user=request.user)

            # Check stock
            for item in cart_items:
                if item.product.stock < item.quantity:
                    messages.error(request, f"Not enough stock for {item.product.name}.")
                    return redirect("cart:cart_view")

            # Create order
            order = Order.objects.create(
                user=request.user,
                full_name=address_obj.full_name,
                phone=address_obj.phone,
                email=address_obj.email,
                address=f"{address_obj.house}, {address_obj.street}, Dalig, Antipolo, Rizal 1870, {address_obj.landmark}",
                status="pending",
            )

            for item in cart_items:
                order.items.create(
                    product=item.product,
                    quantity=item.quantity,
                    price_at_purchase=item.product.price,
                )
                item.product.stock -= item.quantity
                item.product.save()

            # Remove purchased items
            cart.items.filter(id__in=[i.id for i in cart_items]).delete()

            # Clear selected address after placing order
            request.session.pop("selected_address_id", None)

            messages.success(request, "Your order has been placed successfully!")
            return redirect("orders:my_orders")
    
    context = {
        "cart_items": cart_items,
        "items_total": items_total,
        "shop_discount": shop_discount,
        "subtotal": subtotal,
        "shipping_fee": shipping_fee,
        "final_total": final_total,
        "addresses": request.user.addresses.all(),
        "default_address": default_address,
    }
    return render(request, "main/user_checkout.html", context)

@login_required
def save_address(request):
    if request.method == "POST":
        edit_id = request.POST.get("edit_address_id")

        fname = request.POST.get("fname")
        lname = request.POST.get("lname")
        full_name = f"{fname} {lname}".strip()

        phone = request.POST.get("phone")
        email = request.POST.get("email")
        house = request.POST.get("house")
        street = request.POST.get("street")
        landmark = request.POST.get("landmark", "").strip()
        
        # Landmark Dups Issue
        if landmark.lower().startswith("landmark:"):
            landmark = landmark[len("landmark:"):].strip()
        
        label = request.POST.get("label", "Home")
        

        if full_name and phone:
            if edit_id:  # 🟢 update existing
                address = get_object_or_404(UserAddress, id=edit_id, user=request.user)
                address.full_name = full_name
                address.phone = phone
                address.email = email
                address.house = house
                address.street = street
                address.landmark = landmark
                address.label = label
                address.save()
                request.session["selected_address_id"] = address.id
                messages.success(request, "Address updated successfully.")
            else:  # 🆕 create new
                new_addr = request.user.addresses.create(
                    full_name=full_name,
                    phone=phone,
                    email=email,
                    house=house,
                    street=street,
                    landmark=landmark,
                    label=label,
                )
                request.session["selected_address_id"] = new_addr.id
                messages.success(request, "Address saved successfully.")
        else:
            messages.error(request, "Please provide name and phone.")

        return redirect(request.POST.get("next", "orders:checkout"))





# Test for Design
from django.shortcuts import render

def orders_page(request):
    return render(request, "main/orders.html")  # this is your design-only template



@login_required
def delete_address(request, address_id):
    address = get_object_or_404(UserAddress, id=address_id, user=request.user)
    address.delete()
    messages.success(request, "Address deleted successfully.")
    return redirect("orders:checkout")




def order_monitoring(request):
    return render(request, "main/order_monitoring.html")






