from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from products.models import Product, Category
from products.forms import ProductForm, CategoryForm, ProductEditForm
from orders.models import Order
from orders.models import OrderItem
from orders.models import UserAddress
from django.db.models import Sum, Count, F, FloatField, ExpressionWrapper
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.db.models import Sum, F, FloatField
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from products.models import Category



def staff_required(user):
    return user.is_staff

@login_required
@user_passes_test(staff_required, login_url='main:home')
def dashboard(request):
    if request.method == 'POST' and 'add_category' in request.POST:
        cat_form = CategoryForm(request.POST)
        if cat_form.is_valid():
            cat_form.save()
            return redirect('adminpanel:dashboard')
    else:
        cat_form = CategoryForm()

    if request.method == 'POST' and 'add_product' in request.POST:
        prod_form = ProductForm(request.POST, request.FILES)
        if prod_form.is_valid():
            prod_form.save()
            return redirect('adminpanel:dashboard')
    else:
        prod_form = ProductForm()

    # Fetch all products, categories, and recent orders
    products = Product.objects.all()
    categories = Category.objects.all()
    orders = Order.objects.all().order_by('-created_at')[:10]  # Show latest 10 orders
    addresses = UserAddress.objects.all()
    
    # Summary statistics
    total_sales = OrderItem.objects.aggregate(total=Sum(F('quantity') * F('price_at_purchase'), output_field=FloatField()))['total'] or 0
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status="pending").count()
    completed_orders = Order.objects.filter(status="completed").count()
    total_customers = Order.objects.values('user').distinct().count()
    
    # Sales over time (monthly)
    sales_per_month = (
    OrderItem.objects
    .annotate(month=TruncMonth('order__created_at'))
    .values('month')
    .annotate(
        total=Sum(
            ExpressionWrapper(
                F('quantity') * F('price_at_purchase'),
                output_field=FloatField()
            )
        )
    )
    .order_by('month')
    )

    sales_labels = [s['month'].strftime("%b %Y") for s in sales_per_month]
    sales_values = [float(s['total'] or 0) for s in sales_per_month]  # handle None totals
    
    # DEBUG: check what is being sent to the template
    print("Sales labels:", sales_labels)
    print("Sales values:", sales_values)
    print("Total sales:", total_sales)
    
    context = {
        "cat_form": cat_form,
        "prod_form": prod_form,
        "products": products,
        "categories": categories,
        "recent_orders": orders,
        "orders": orders,
        "addresses": addresses,
        "total_sales": total_sales,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "completed_orders": completed_orders,
        "total_customers": total_customers,
        "sales_labels": json.dumps(sales_labels),
        "sales_values": json.dumps(sales_values),
    }

    return render(request, "adminpanel/admin_dashboard.html", context)

def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect('adminpanel:dashboard')

@csrf_exempt  # Optional if you handle CSRF in fetch headers
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        print("🔹 Incoming POST:", request.POST)
        print("🔹 Incoming FILES:", request.FILES)

        form = ProductEditForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            print("✅ Product updated:", product.name)
            return JsonResponse({"success": True})
        else:
            print("❌ Form errors:", form.errors)
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)

def export_pdf(request):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="admin_report.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    sales_per_month = (
        OrderItem.objects
        .annotate(month=TruncMonth('order__created_at'))
        .values('month')
        .annotate(
            total=Sum(
                ExpressionWrapper(
                    F('quantity') * F('price_at_purchase'),
                    output_field=FloatField()
                )
            )
        )
        .order_by('month')
    )

    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status="pending").count()
    completed_orders = Order.objects.filter(status="completed").count()
    total_customers = Order.objects.values('user').distinct().count()

    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 100, "Admin Dashboard Report")

    p.setFont("Helvetica", 12)
    p.drawString(100, height - 140, f"Total Orders: {total_orders}")
    p.drawString(100, height - 160, f"Pending Orders: {pending_orders}")
    p.drawString(100, height - 180, f"Completed Orders: {completed_orders}")
    p.drawString(100, height - 200, f"Total Customers: {total_customers}")

    y = height - 240
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, y, "Monthly Sales:")

    p.setFont("Helvetica", 12)
    y -= 20
    for s in sales_per_month:
        month_label = s['month'].strftime("%B %Y")
        total = float(s['total'] or 0)
        p.drawString(120, y, f"{month_label}: ${total:,.2f}")
        y -= 20
        if y < 100:
            p.showPage()
            y = height - 100
            p.setFont("Helvetica", 12)

    p.showPage()
    p.save()
    return response








# ========================
# New Admin Dashboard Logic
# ========================

@login_required
@user_passes_test(staff_required, login_url='main:home')
def custom_admin_dashboard(request):
    categories = get_categories()
    products = Product.objects.select_related("category").all().order_by("id")  # ✅ Fetch products

    context = {
        "title": "Custom Admin Dashboard",
        "categories": categories,
        "products": products,  # ✅ Add products to context
    }
    return render(request, "adminpanel/admin_dashboard.html", context)





# === Add/Edit Category ===
@login_required
@user_passes_test(staff_required, login_url='main:home')
def create_category(request):
    if request.method == "POST":
        name = request.POST.get("category-name")
        slug = request.POST.get("category-slug")
        category_id = request.POST.get("category-id")  # hidden input

        if name and slug:
            if category_id:  # Edit mode
                cat = Category.objects.get(id=category_id)
                cat.name = name
                cat.slug = slug
                cat.save()
            else:  # Add mode
                Category.objects.create(name=name, slug=slug)

        return redirect("adminpanel:custom_dashboard")  # ✅ back to dashboard

    return redirect("adminpanel:custom_dashboard")



# === Validate when adding/editing ===#
def validate_category(request):
    name = request.GET.get("name", "").strip()
    slug = request.GET.get("slug", "").strip()
    category_id = request.GET.get("id")  # new

    errors = {}

    qs_name = Category.objects.filter(name__iexact=name)
    qs_slug = Category.objects.filter(slug__iexact=slug)

    if category_id:
        qs_name = qs_name.exclude(id=category_id)
        qs_slug = qs_slug.exclude(id=category_id)

    if name and qs_name.exists():
        errors["name"] = "Category name is already taken."

    if slug and qs_slug.exists():
        errors["slug"] = "Category slug is already taken."

    return JsonResponse({"errors": errors})


# === Helper for fetching categories ===
def get_categories():
    """Fetch all categories with product counts."""
    return (
        Category.objects
        .annotate(product_count=Count("product"))
        .order_by("name")
    )
    

# === Delete Category ===
@login_required
@user_passes_test(staff_required, login_url='main:home')
def delete_category(request, pk):
    if request.method == "POST":  # safety: only allow POST
        try:
            cat = Category.objects.get(pk=pk)
            cat.delete()
        except Category.DoesNotExist:
            pass  # or handle with a message
    return redirect("adminpanel:custom_dashboard")






