from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from cart.models import CartItem, Cart
from products.models import Product
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Cart, CartItem  # cart app models
import json
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta


@login_required
def cart_view(request):
    expiry_cutoff = timezone.now() - timedelta(hours=24)
    CartItem.objects.filter(reserved_at__lt=expiry_cutoff).delete()
    cart_items = CartItem.objects.filter(cart__user=request.user)

    # Annotate each item with subtotal (for JS to read)
    for item in cart_items:
        item.subtotal = item.product.price * item.quantity  # optional, can remove if JS reads from price/unit
        item.expires_at = item.reserved_at + timedelta(hours=24)

    context = {
        "cart_items": cart_items,
        "now": timezone.now(),
    }
    return render(request, "main/user_cart.html", context)



@require_POST
def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        return redirect('/?show_login=1')

    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    # Get or create a cart for the user
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Calculate quantity already reserved in OTHER users' carts
    expiry_cutoff = timezone.now() - timedelta(hours=24)
    reserved_by_others = reserved_quantity(product, exclude_user=request.user)

    available_for_user = product.stock - reserved_by_others
    if available_for_user <= 0:
        messages.error(request, f"Sorry, {product.name} has been fully reserved by other customers.")
        return redirect(request.POST.get('next') or 'products:product_detail', product_id=product.id)

    # Add or update cart item for this user, but respect available_for_user
    cart_item = CartItem.objects.filter(cart=cart, product=product).first()

    if cart_item:
        new_quantity = cart_item.quantity + quantity
        if new_quantity > available_for_user:
            messages.error(request, f"Only {available_for_user} of {product.name} available right now.")
            return redirect(request.POST.get('next') or 'products:product_detail', product_id=product.id)
        cart_item.quantity = new_quantity
        # renew reservation timestamp when user updates their cart
        cart_item.reserved_at = timezone.now()
        cart_item.save()
    else:
        if quantity > available_for_user:
            messages.error(request, f"Only {available_for_user} of {product.name} available right now.")
            return redirect(request.POST.get('next') or 'products:product_detail', product_id=product.id)
        cart_item = CartItem.objects.create(cart=cart, product=product, quantity=quantity)
        cart_item.reserved_at = timezone.now()
        cart_item.save()

    cart_item.save()

    next_url = request.POST.get('next')
    if next_url:
        return redirect(next_url)
    else:
        return redirect('products:product_detail', product_id=product.id)



@require_POST
def add_to_cart_api(request):
    if not request.user.is_authenticated:
        return redirect('/?show_login=1')

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))

    if not product_id:
        return JsonResponse({'success': False, 'error': 'no_product_id'}, status=400)

    product = get_object_or_404(Product, id=product_id)

    expiry_cutoff = timezone.now() - timedelta(hours=24)
    reserved_by_others = reserved_quantity(product, exclude_user=request.user)

    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    # 👇 Adjust available stock to include the user's current reservation (if any)
    available_stock = product.stock - reserved_by_others + (cart_item.quantity if not created else 0)

    if available_stock <= 0:
        return JsonResponse({
            'success': False,
            'error': 'insufficient_stock',
            'message': f'{product.name} is currently reserved by other customers.'
        }, status=400)

    # If adding new quantity exceeds available, block it
    if cart_item.quantity + quantity > available_stock:
        return JsonResponse({
            'success': False,
            'error': 'insufficient_stock',
            'message': f'Only {available_stock - cart_item.quantity} more {product.name}(s) can be added right now.'
        }, status=400)

    # ✅ Update quantity safely
    cart_item.quantity += quantity
    cart_item.reserved_at = timezone.now()
    cart_item.save()

    return JsonResponse({'success': True, 'message': f'Added {product.name} to cart'})


@csrf_exempt
@require_POST
def update_cart_item(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        quantity = int(data.get('quantity', 1))
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid data'}, status=400)

    try:
        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        product = cart_item.product

        # Reserved by others
        expiry_cutoff = timezone.now() - timedelta(hours=24)
        reserved_by_others = reserved_quantity(product, exclude_user=request.user)

        # 👇 Allow the user's current reservation in the total
        available_for_user = product.stock - reserved_by_others + cart_item.quantity

        if available_for_user <= 0:
            cart_item.delete()
            return JsonResponse({
                'success': False,
                'message': f"{product.name} is no longer available and was removed from your cart."
            }, status=400)

        # Clamp quantity to the allowed range
        if quantity < 1:
            quantity = 1
        if quantity > available_for_user:
            quantity = available_for_user

        cart_item.quantity = quantity
        cart_item.reserved_at = timezone.now()
        cart_item.save()

        subtotal = cart_item.product.price * cart_item.quantity
        total = sum(i.product.price * i.quantity for i in CartItem.objects.filter(cart__user=request.user))
        final_total = total

        return JsonResponse({
            'success': True,
            'subtotal': float(subtotal),
            'total': float(total),
            'final_total': float(final_total)
        })

    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Cart item not found'}, status=404)

    
@require_POST
def delete_cart_item(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Authentication required.'}, status=403)
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        cart_item.delete()
        return JsonResponse({'success': True})
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Item not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@require_POST
@login_required
def check_stock(request):
    try:
        data = json.loads(request.body)
        items = data.get('items', [])
    except Exception:
        return JsonResponse({'success': False, 'message': 'Invalid request data.'}, status=400)
    
    for entry in items:
        try:
            cart_item = CartItem.objects.select_related('product').get(
                id=entry['id'],
                cart__user=request.user  # ✅ FIXED: match via cart__user
            )
            if entry['quantity'] > cart_item.product.stock:
                return JsonResponse({
                    'success': False,
                    'message': f"Not enough stock for {cart_item.product.name}. Only {cart_item.product.stock} left."
                })
        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Cart item not found.'}, status=404)
    
    return JsonResponse({'success': True})

def reservation_cutoff(hours=24):
    return timezone.now() - timedelta(hours=hours)

def reserved_quantity(product, exclude_user=None, hours=24):
    cutoff = reservation_cutoff(hours)
    qs = CartItem.objects.filter(product=product, reserved_at__gte=cutoff)
    if exclude_user:
        qs = qs.exclude(cart__user=exclude_user)
    return qs.aggregate(total=Sum('quantity'))['total'] or 0