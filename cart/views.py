from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from cart.models import CartItem, Cart
from products.models import Product
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Cart, CartItem  # cart app models
import json

def cart_view(request):
    if not request.user.is_authenticated:
        # Redirect to home with a query param to show login modal
        return redirect('/?show_login=1')

    cart_items = CartItem.objects.filter(cart__user=request.user)

    for item in cart_items:
        item.subtotal = item.product.price * item.quantity

    total = sum(item.subtotal for item in cart_items)

    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'shared/cart.html', context)


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


