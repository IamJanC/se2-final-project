from django.shortcuts import get_object_or_404
from .models import Product

# Logic-only function to fetch all products (for use in main/views.py)
def get_all_products():
    products = Product.objects.select_related('category').all()
    return products




# Optional: You can keep this if you want a product detail page under /products/<id>/
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'main/product_detail.html', {'product': product})

