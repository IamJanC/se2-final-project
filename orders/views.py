from django.shortcuts import render,get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages  # ✅ Add this
from .models import Order

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'main/my_orders.html', {'orders': orders})

@login_required
def create_order(request):
    if request.method == 'POST':
        product = request.POST.get('product')
        quantity = request.POST.get('quantity')
        address = request.POST.get('address')

        Order.objects.create(
            user=request.user,
            product=product,
            quantity=quantity,
            address=address
        )

        messages.success(request, 'Order placed successfully!')  # ✅ Add this before redirect
        return redirect('my_orders')

    return render(request, 'main/create_order.html')
