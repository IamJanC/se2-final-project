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




@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(cart__user=request.user)

    # Annotate each item with subtotal (for JS to read)
    for item in cart_items:
        item.subtotal = item.product.price * item.quantity  # optional, can remove if JS reads from price/unit

    context = {
        "cart_items": cart_items,
    }
    return render(request, "main/user_cart.html", context)




@require_POST
def add_to_cart(request, product_id):



    if not request.user.is_authenticated:
        # Redirect unauthenticated users to home with login modal
        return redirect('/?show_login=1')

    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    # Get or create a cart for the user
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Add or update cart item
    cart_item = CartItem.objects.filter(cart=cart, product=product).first()
    
    if cart_item:
        new_quantity = cart_item.quantity + quantity

        #if cart_item.quantity >= product.stock:
            #messages.error(request, f"You already have the maximum stock ({product.stock}) of {product.name} in your cart.")
            #return redirect(request.POST.get('next') or 'products:product_detail', product_id=product.id)

        if cart_item.quantity >= product.stock:
            return redirect(request.POST.get('next') or 'products:product_detail', product_id=product.id)

        
        if new_quantity > product.stock:
            messages.error(request, f"Only {product.stock} of {product.name} available.")
            return redirect(request.POST.get('next') or 'products:product_detail', product_id=product.id)

        cart_item.quantity = new_quantity

    else:
        if quantity > product.stock:
            messages.error(request, f"Only {product.stock} of {product.name} available.")
            return redirect(request.POST.get('next') or 'products:product_detail', product_id=product.id)
        
        cart_item = CartItem.objects.create(cart=cart, product=product, quantity=quantity)

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