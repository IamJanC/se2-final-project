from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test, login_required
from products.models import Product
from orders.models import Order


# Allow only staff users to access

def staff_required(user):
    return user.is_staff

@login_required
@user_passes_test(staff_required, login_url='main:home')
@user_passes_test(lambda u: u.is_staff)
def dashboard(request):
    products = Product.objects.all()
    orders = Order.objects.all()

    return render(request, 'adminpanel/admin.html', {
        'products': products,
        'orders': orders
    })
