from django.shortcuts import render                 # type: ignore
from products.models import Product
from orders.models import Order
from django.contrib import messages
from django.shortcuts import get_object_or_404  
from products.views import get_all_products  # import logic layer for product gallery


def home(request):
    return render(request, 'main/home.html')

def product(request):
    return render(request, 'main/product.html')

# Gallery Rendering 
def shop(request):
    products = get_all_products()
    return render(request, 'main/gallery.html', {'products': products})

# Product Description Rendering
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)  # 🔄 Use this instead
    return render(request, 'main/productTemp.html', {'product': product})




# will fix this later
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

