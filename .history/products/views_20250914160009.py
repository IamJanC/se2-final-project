from django.shortcuts import get_object_or_404
from .models import Product

#For search
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Q

import json
from django.views.decorators.http import require_POST


from django.shortcuts import render


# Logic-only function to fetch all products (for use in main/views.py)
def get_all_products():
    products = Product.objects.select_related('category').all()
    return products


# Logic for search
def search_products(request):
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        qs = Product.objects.filter(
            name__icontains=query
        ).distinct()[:8]

        for p in qs:
            results.append({
                'id': p.id,
                'name': p.name,
                'url': f'/shop/{p.id}/',          # direct, safe URL for your setup
                'price': str(p.price) if hasattr(p, 'price') else None,
                'image': p.image_url or None
            })

    return JsonResponse(results, safe=False)

#Logic for miniview
def product_detail_json(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    data = {
        'id': product.id,
        'name': product.name,
        'price': str(product.price),
        'category': product.category.name if product.category else '',
        'stock': product.stock,
        'description': product.description or '',
        'image_url': product.image_url or ''
    }
    return JsonResponse(data)


# Logic for product_listing - created after developing the search feature (temp)
def product_list(request):
    products = Product.objects.all()
    return render(request, 'main/product_list.html', {'products': products})


# Optional: You can keep this if you want a product detail page under /products/<id>/
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    cart_item = None
    if request.user.is_authenticated:
        cart_item = CartItem.objects.filter(cart_user=request.user, product=product).first()
    
    return render(request, 'main/product.html', {
        'product': product,
        'cart_item': cart_item,
    })




