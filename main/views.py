from django.shortcuts import render                 # type: ignore
from products.models import Product
from orders.models import Order
from django.contrib import messages

def home(request):
    print(f"[DEBUG] request.user: {request.user}")
    print(f"[DEBUG] Is authenticated: {request.user.is_authenticated}")
    return render(request, 'main/home.html')

def product(request):
    return render(request, 'main/product.html')

def shop(request):
    return render(request, 'main/gallery.html')  # <- rename your HTML to gallery.html

def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))

        product = get_object_or_404(Product, id=product_id)

        Order.objects.create(
            user=request.user,
            product=product,
            quantity=quantity,
            status='Pending'
        )

        messages.success(request, 'Order placed successfully!')  # ✅ Add this
        return redirect('home')

