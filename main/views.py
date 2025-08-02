from django.shortcuts import render                 # type: ignore

def home(request):
    print(f"[DEBUG] request.user: {request.user}")
    print(f"[DEBUG] Is authenticated: {request.user.is_authenticated}")
    return render(request, 'main/home.html')

def product(request):
    return render(request, 'main/product.html')

