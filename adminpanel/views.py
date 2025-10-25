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
from django.utils import timezone
from datetime import timedelta



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


# ========================
# Dashboard View
# ========================
@login_required
@user_passes_test(staff_required, login_url='main:home')
def dashboard_view(request):
    """Displays the main admin dashboard with categories, products, and order stats."""

    # -----------------------------
    # Categories & Products
    # -----------------------------
    categories = Category.objects.all()
    products = Product.objects.select_related("category").all().order_by("id")

    # Low stock products
    low_stock_products = products.filter(stock__lt=20).order_by("stock")

    # -----------------------------
    # Pending & Cancelled Orders (Last 30 days)
    # -----------------------------
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    sixty_days_ago = now - timedelta(days=60)

    # Pending orders (last 30 days)
    pending_orders_count = Order.objects.filter(status="pending", created_at__gte=thirty_days_ago).count()
    pending_orders_users_count = Order.objects.filter(status="pending", created_at__gte=thirty_days_ago).values("user").distinct().count()
    
    # Cancelled orders (last 30 days vs previous 30 days)
    current_cancelled_orders_count = Order.objects.filter(status="cancelled", created_at__gte=thirty_days_ago).count()
    previous_cancelled_orders_count = Order.objects.filter(
        status="cancelled",
        created_at__gte=sixty_days_ago,
        created_at__lt=thirty_days_ago
    ).count()

    # Calculate cancelled orders % change - FIXED LOGIC
    cancelled_change_percent = 0
    if previous_cancelled_orders_count > 0:
        cancelled_change_percent = round(
            ((current_cancelled_orders_count - previous_cancelled_orders_count) / previous_cancelled_orders_count) * 100, 1
        )
    elif current_cancelled_orders_count > 0:
        cancelled_change_percent = 100.0

    # FIXED: Always show the actual percentage value (positive or negative)
    cancelled_change_percent_up = cancelled_change_percent if cancelled_change_percent > 0 else 0
    cancelled_change_percent_down = abs(cancelled_change_percent) if cancelled_change_percent < 0 else 0

    # -----------------------------
    # Total Orders (Last 30 days vs Previous 30 days) - FIXED
    # -----------------------------
    # Current 30-day period
    current_orders_count = Order.objects.filter(created_at__gte=thirty_days_ago).count()

    # Previous 30-day period
    previous_orders_count = Order.objects.filter(
        created_at__gte=sixty_days_ago,
        created_at__lt=thirty_days_ago
    ).count()

    # Calculate % change - FIXED: Handle case when both are 0
    orders_change_percent = 0
    if previous_orders_count > 0:
        orders_change_percent = round(
            ((current_orders_count - previous_orders_count) / previous_orders_count) * 100, 1
        )
    elif current_orders_count > 0:
        orders_change_percent = 100.0  # new orders this period
    # If both are 0, orders_change_percent remains 0

    # FIXED: Show actual values - if percentage is positive, show in up; if negative, show in down
    orders_change_percent_up = orders_change_percent if orders_change_percent > 0 else 0
    orders_change_percent_down = abs(orders_change_percent) if orders_change_percent < 0 else 0

    # -----------------------------
    # Context
    # -----------------------------
    context = {
        "title": "Dashboard",
        "categories": categories,
        "products": products,
        "low_stock_products": low_stock_products,

        # Pending & Cancelled Orders (last 30 days)
        "pending_orders_count": pending_orders_count,
        "pending_orders_users_count": pending_orders_users_count,
        "cancelled_orders_count": current_cancelled_orders_count,
        
        # Cancelled orders change
        "cancelled_change_percent_up": cancelled_change_percent_up,
        "cancelled_change_percent_down": cancelled_change_percent_down,

        # Total Orders
        "current_orders_count": current_orders_count,
        "previous_orders_count": previous_orders_count,
        "orders_change_percent_up": orders_change_percent_up,
        "orders_change_percent_down": orders_change_percent_down,
        
        # DEBUG: Add the raw percentage for troubleshooting
        "orders_change_percent_raw": orders_change_percent,
    }

    return render(request, "adminpanel/main/dashboard.html", context)




# ========================
# PRODUCTS PAGE VIEW
# ========================
@login_required
@user_passes_test(staff_required, login_url='main:home')
def products_view(request):
    """Displays all products and their categories in the Products tab."""
    categories = get_categories()
    products = Product.objects.select_related("category").all().order_by("id")

    context = {
        "title": "Products",
        "categories": categories,
        "products": products,
    }

    return render(request, "adminpanel/main/products.html", context)


# ========================
# CATEGORY MANAGEMENT
# ========================
@login_required
@user_passes_test(staff_required, login_url='main:home')
def create_category(request):
    """Handles both adding and editing categories."""
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

        # ✅ After adding or editing, go back to Products page
        return redirect("adminpanel:products")

    return redirect("adminpanel:products")


@login_required
@user_passes_test(staff_required, login_url='main:home')
def delete_category(request, pk):
    """Deletes a category safely."""
    if request.method == "POST":
        try:
            cat = Category.objects.get(pk=pk)
            cat.delete()
        except Category.DoesNotExist:
            pass
    return redirect("adminpanel:products")


def validate_category(request):
    """AJAX validation for unique category name/slug."""
    name = request.GET.get("name", "").strip()
    slug = request.GET.get("slug", "").strip()
    category_id = request.GET.get("id")

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


# ========================
# Helper Function
# ========================
def get_categories():
    """Fetch all categories with product counts."""
    return (
        Category.objects
        .annotate(product_count=Count("product"))
        .order_by("name")
    )




# ========================
# Admin Orders Section
# ========================
@login_required
@user_passes_test(staff_required, login_url='main:home')
def admin_orders(request):
    """Displays all orders inside the Admin Dashboard (Orders page)."""
    orders = (
        Order.objects
        .select_related("user")
        .prefetch_related("items__product")
        .annotate(
            total_amount=Sum(
                ExpressionWrapper(
                    F("items__price_at_purchase") * F("items__quantity"),
                    output_field=FloatField()
                )
            )
        )
        .order_by("-created_at")
    )

    context = {
        "orders": orders,
    }

    # Render the new template under templates/main/
    return render(request, "adminpanel/main/orders.html", context)



