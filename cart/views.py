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



def cart_view(request):
    if not request.user.is_authenticated:
        return redirect('/?show_login=1')

    cart_items = CartItem.objects.filter(cart__user=request.user)

    total = 0
    for item in cart_items:
        item.subtotal = item.product.price * item.quantity
        total += item.subtotal

    # Hardcoded for now
    discount = 500
    shipping_fee = 100

    subtotal_after_discount = max(total - discount, 0)  # ensure not negative
    final_total = subtotal_after_discount + shipping_fee

    context = {
        'cart_items': cart_items,
        'total': total,
        'discount': discount,
        'shipping_fee': shipping_fee,
        'subtotal_after_discount': subtotal_after_discount,
        'final_total': final_total,
    }
    return render(request, 'main/user_cart.html', context)



@require_POST
def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        # Redirect unauthenticated users to home with login modal
        return redirect('/?show_login=1')

    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    # Get or create a cart for the user
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Check if item already in cart
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity

    cart_item.save()
    messages.success(request, f"{product.name} added to cart.")

    # Redirect back to 'next' URL if provided, else fallback to product detail
    next_url = request.POST.get('next')
    if next_url:
        return redirect(next_url)
    else:
        return redirect('products:product_detail', product_id=product.id)


#add to cart API - for miniview
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

    if product.stock < quantity:
        return JsonResponse({'success': False, 'error': 'insufficient_stock', 'message': 'Not enough stock.'}, status=400)

    # Get or create cart for the user
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Add or update cart item with quantity increment
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
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
        if quantity < 1:
            quantity = 1
        if quantity > cart_item.product.stock:
            quantity = cart_item.product.stock
        cart_item.quantity = quantity
        cart_item.save()

        subtotal = cart_item.product.price * cart_item.quantity
        total = sum(i.product.price * i.quantity for i in CartItem.objects.filter(cart__user=request.user))
        final_total = total  # can include shipping/discount logic if needed

        return JsonResponse({
            'success': True,
            'subtotal': float(subtotal),
            'total': float(total),
            'final_total': float(final_total)
        })
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Cart item not found'}, status=404)