from django.shortcuts import render, get_object_or_404
from .models import Product

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'main/product_detail.html', {'product': product})

# View for product list
def product_list(request):
    products = Product.objects.select_related('category').all()
    return render(request, 'main/gallery.html', {'products': products})