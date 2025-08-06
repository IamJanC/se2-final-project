from django.shortcuts import render                 # type: ignore
from products.models import Product
from orders.models import Order
from django.contrib import messages
from django.shortcuts import get_object_or_404  
from products.views import get_all_products  # import logic layer for product gallery
from collections import defaultdict
from products.models import Category, Product


def get_home_context():
    from collections import defaultdict
    products_by_category = defaultdict(list)
    
    categories = Category.objects.all()
    for category in categories:
        products = Product.objects.filter(category=category)[:5]
        if products.exists():
            products_by_category[category] = products

    return {
        'products_by_category': dict(products_by_category)
    }



def home(request):
    context = get_home_context()
    return render(request, 'main/home.html', context)

    
def product(request):
    return render(request, 'main/product.html')

def shop(request):
    category_slug = request.GET.get('category')

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category)
    else:
        products = get_all_products()

    return render(request, 'main/gallery.html', {
        'products': products,
        'selected_category': category_slug
    })


# Product Description Rendering
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)  # 🔄 Use this instead
    return render(request, 'main/product.html', {'product': product})




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

