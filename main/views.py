from django.shortcuts import render                 # type: ignore
from products.models import Product, Category
from orders.models import Order
from django.contrib import messages
from django.shortcuts import get_object_or_404, render  
from products.views import get_all_products  # import logic layer for product gallery
from collections import defaultdict
from django.db.models import Min, Max, Count

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
    products = Product.objects.all()
    
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    else:
        category = None

    sort = request.GET.get('sort')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'rating':
        products = products.order_by('-rating')
    else:
        products = products.order_by('-id')

    price_max = request.GET.get('price_max')
    if price_max:
        products = products.filter(price__lte=price_max)

    
    categories = Category.objects.annotate(product_count=Count('product'))
    price_range = Product.objects.aggregate(
        min_price=Min('price'),
        max_price=Max('price')
    )

    return render(request, 'main/gallery.html', {
        'products': products,
        'categories': categories,
        'min_price': price_range['min_price'],
        'max_price': price_range['max_price'],
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
    
def admin_dashboard(request):
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:5]  # last 5 orders
    return render(request, 'main/admin.html')

