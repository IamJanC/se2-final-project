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
from django.contrib.auth import get_user_model
from django.contrib.admin.views.decorators import staff_member_required
from products.models import Product
from orders.models import Order
from django.db.models import Sum, F, FloatField, ExpressionWrapper
from datetime import datetime


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
# Dashboard View - FINAL CORRECTED VERSION FOR YOUR MODELS
# ========================
# Required imports (add at top of your views.py if not already there)
from django.db.models import Sum, Count, Q, F, FloatField
from decimal import Decimal

@login_required
@user_passes_test(staff_required, login_url='main:home')
def dashboard_view(request):
    """Displays the main admin dashboard with categories, products, and order stats."""

    now = timezone.now()
    seven_days_ago = now - timedelta(days=7)
    thirty_days_ago = now - timedelta(days=30)
    sixty_days_ago = now - timedelta(days=60)

    # -----------------------------
    # Categories & Products
    # -----------------------------
    categories = Category.objects.all()
    products = Product.objects.select_related("category").all().order_by("id")

    # Low stock products (stock < 20) - Uses 'stock' field
    low_stock_products = products.filter(stock__lt=20).order_by("stock")[:5]

    # -----------------------------
    # TOTAL SALES (Last 30 days vs Previous 30 days)
    # -----------------------------
    # Current 30 days sales - FIXED: Calculate from OrderItems
    current_sales = OrderItem.objects.filter(
        order__created_at__gte=thirty_days_ago,
        order__status__in=['completed', 'shipped', 'delivered']
    ).aggregate(
        total=Sum(F('quantity') * F('price_at_purchase'), output_field=FloatField())
    )['total'] or Decimal('0.00')

    # Previous 30 days sales - FIXED: Calculate from OrderItems
    previous_sales = OrderItem.objects.filter(
        order__created_at__gte=sixty_days_ago,
        order__created_at__lt=thirty_days_ago,
        order__status__in=['completed', 'shipped', 'delivered']
    ).aggregate(
        total=Sum(F('quantity') * F('price_at_purchase'), output_field=FloatField())
    )['total'] or Decimal('0.00')

    # Calculate sales % change
    sales_change_percent = 0
    if previous_sales > 0:
        sales_change_percent = round(
            ((current_sales - previous_sales) / previous_sales) * 100, 1
        )
    elif current_sales > 0:
        sales_change_percent = 100.0

    sales_change_percent_up = sales_change_percent if sales_change_percent > 0 else 0
    sales_change_percent_down = abs(sales_change_percent) if sales_change_percent < 0 else 0

    # -----------------------------
    # TOTAL ORDERS (Last 30 days vs Previous 30 days)
    # -----------------------------
    current_orders_count = Order.objects.filter(created_at__gte=thirty_days_ago).count()
    previous_orders_count = Order.objects.filter(
        created_at__gte=sixty_days_ago,
        created_at__lt=thirty_days_ago
    ).count()

    # Calculate orders % change
    orders_change_percent = 0
    if previous_orders_count > 0:
        orders_change_percent = round(
            ((current_orders_count - previous_orders_count) / previous_orders_count) * 100, 1
        )
    elif current_orders_count > 0:
        orders_change_percent = 100.0

    orders_change_percent_up = orders_change_percent if orders_change_percent > 0 else 0
    orders_change_percent_down = abs(orders_change_percent) if orders_change_percent < 0 else 0

    # -----------------------------
    # PENDING & CANCELLED ORDERS (Last 30 days)
    # -----------------------------
    pending_orders_count = Order.objects.filter(
        status="pending",
        created_at__gte=thirty_days_ago
    ).count()
    
    pending_orders_users_count = Order.objects.filter(
        status="pending",
        created_at__gte=thirty_days_ago
    ).values("user").distinct().count()
    
    # Cancelled orders (current vs previous period)
    current_cancelled_orders_count = Order.objects.filter(
        status="cancelled",
        created_at__gte=thirty_days_ago
    ).count()
    
    previous_cancelled_orders_count = Order.objects.filter(
        status="cancelled",
        created_at__gte=sixty_days_ago,
        created_at__lt=thirty_days_ago
    ).count()

    # Calculate cancelled orders % change
    cancelled_change_percent = 0
    if previous_cancelled_orders_count > 0:
        cancelled_change_percent = round(
            ((current_cancelled_orders_count - previous_cancelled_orders_count) / previous_cancelled_orders_count) * 100, 1
        )
    elif current_cancelled_orders_count > 0:
        cancelled_change_percent = 100.0

    cancelled_change_percent_up = cancelled_change_percent if cancelled_change_percent > 0 else 0
    cancelled_change_percent_down = abs(cancelled_change_percent) if cancelled_change_percent < 0 else 0

    # -----------------------------
    # FAST MOVING PRODUCTS (Last 7 days)
    # -----------------------------
    # Uses price_at_purchase from OrderItem, stock and image_url from Product
    fast_moving_products = OrderItem.objects.filter(
        order__created_at__gte=seven_days_ago,
        order__status__in=['completed', 'shipped', 'delivered', 'pending']
    ).values(
        'product__id',
        'product__name',
        'product__image_url',  # CORRECTED: uses image_url
        'product__price',
        'product__stock'  # CORRECTED: uses stock
    ).annotate(
        total_quantity=Sum('quantity'),
        total_sales=Sum(F('quantity') * F('price_at_purchase'))
    ).order_by('-total_quantity')[:3]

    # Add stock status to fast moving products
    for product in fast_moving_products:
        stock = product['product__stock']  # CORRECTED: uses stock
        if stock == 0:
            product['stock_status'] = 'danger'
            product['stock_label'] = 'Out of Stock'
        elif stock < 20:
            product['stock_status'] = 'warning'
            product['stock_label'] = 'Low Stock'
        else:
            product['stock_status'] = 'success'
            product['stock_label'] = 'In Stock'

    # -----------------------------
    # SLOW MOVING PRODUCTS (Last 7 days)
    # -----------------------------
    # Uses price_at_purchase from OrderItem, stock and image_url from Product
    slow_moving_products = OrderItem.objects.filter(
        order__created_at__gte=seven_days_ago,
        order__status__in=['completed', 'shipped', 'delivered', 'pending']
    ).values(
        'product__id',
        'product__name',
        'product__image_url',  # CORRECTED: uses image_url
        'product__price',
        'product__stock'  # CORRECTED: uses stock
    ).annotate(
        total_quantity=Sum('quantity'),
        total_sales=Sum(F('quantity') * F('price_at_purchase'))
    ).order_by('total_quantity')[:3]

    # Add stock status to slow moving products
    for product in slow_moving_products:
        stock = product['product__stock']  # CORRECTED: uses stock
        if stock == 0:
            product['stock_status'] = 'danger'
            product['stock_label'] = 'Out of Stock'
        elif stock < 20:
            product['stock_status'] = 'warning'
            product['stock_label'] = 'Low Stock'
        else:
            product['stock_status'] = 'success'
            product['stock_label'] = 'In Stock'

    # -----------------------------
    # RECENT TRANSACTIONS (Last 10)
    # -----------------------------
    recent_transactions = Order.objects.select_related('user').order_by('-created_at')[:10]

    # Format transactions for template
    formatted_transactions = []
    for order in recent_transactions:
        # Get status badge class
        if order.status == 'completed' or order.status == 'delivered':
            status_class = 'success'
            status_label = 'Completed'
        elif order.status == 'cancelled':
            status_class = 'danger'
            status_label = 'Cancelled'
        else:
            status_class = 'pending'
            status_label = order.status.capitalize()

        # FIXED: Calculate total from OrderItems
        order_total = OrderItem.objects.filter(order=order).aggregate(
            total=Sum(F('quantity') * F('price_at_purchase'), output_field=FloatField())
        )['total'] or 0

        formatted_transactions.append({
            'customer_id': f'CUST-{order.user.id:03d}',
            'order_date': order.created_at.strftime('%Y-%m-%d'),
            'order_time': order.created_at.strftime('%H:%M'),
            'status_class': status_class,
            'status_label': status_label,
            'amount': order_total
        })

    # -----------------------------
    # RECENT SESSION LOGS (Last 10 logins)
    # -----------------------------
    # Uses recent orders as proxy for user activity
    recent_sessions = []
    recent_user_activities = Order.objects.select_related('user').order_by('-created_at').values(
        'user__id',
        'user__username',
        'created_at'
    ).distinct()[:10]

    for activity in recent_user_activities:
        recent_sessions.append({
            'user_id': activity['user__id'],
            'username': activity['user__username'],
            'time': activity['created_at'].strftime('%H:%M')
        })

    # -----------------------------
    # Context
    # -----------------------------
    context = {
        "title": "Dashboard",
        "categories": categories,
        "products": products,
        "low_stock_products": low_stock_products,

        # Sales Data
        "current_sales": f"{current_sales:,.2f}",
        "previous_sales": f"{previous_sales:,.2f}",
        "sales_change_percent_up": sales_change_percent_up,
        "sales_change_percent_down": sales_change_percent_down,
        "sales_change_percent_raw": sales_change_percent,

        # Orders Data
        "current_orders_count": current_orders_count,
        "previous_orders_count": previous_orders_count,
        "orders_change_percent_up": orders_change_percent_up,
        "orders_change_percent_down": orders_change_percent_down,
        "orders_change_percent_raw": orders_change_percent,

        # Pending & Cancelled Orders
        "pending_orders_count": pending_orders_count,
        "pending_orders_users_count": pending_orders_users_count,
        "cancelled_orders_count": current_cancelled_orders_count,
        "cancelled_change_percent_up": cancelled_change_percent_up,
        "cancelled_change_percent_down": cancelled_change_percent_down,

        # Product Movement
        "fast_moving_products": fast_moving_products,
        "slow_moving_products": slow_moving_products,

        # Recent Activity
        "recent_transactions": formatted_transactions,
        "recent_sessions": recent_sessions,
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

@login_required
@user_passes_test(staff_required, login_url='main:home')
@csrf_exempt
def save_product(request):
    if request.method != "POST":
        return JsonResponse(
            {"status": "error", "message": "Invalid request method."},
            status=405
        )

    try:
        data = request.POST

        custom_id = data.get("custom_id", "").strip()
        name = data.get("name", "")
        description = data.get("description", "")
        price = data.get("price", "")
        discount_price = data.get("discount_price", "")
        discount_start = data.get("discount_start", "")
        discount_end = data.get("discount_end", "")
        stock_quantity = data.get("stock_quantity", "")
        stock_status = data.get("stock_status", "")
        category = data.get("category", "")
        image_url = data.get("image_url", "")

        category_instance = None
        if category:
            try:
                category_instance = Category.objects.get(id=category)
            except Category.DoesNotExist:
                return JsonResponse({
                    "status": "error",
                    "message": f"Category with id {category} does not exist."
                }, status=400)

        product = Product.objects.filter(custom_id=custom_id).first()
        if product:
            product.name = name
            product.description = description
            product.price = price
            product.discount_price = discount_price
            product.discount_start = discount_start or None
            product.discount_end = discount_end or None
            product.stock_quantity = stock_quantity
            product.stock_status = stock_status
            product.category = category_instance
            product.image_url = image_url
            product.save()

            return JsonResponse({
                "status": "success",
                "message": f"Product '{product.name}' (ID: {product.custom_id}) updated successfully!"
            })

        product = Product.objects.create(
            custom_id=custom_id,
            name=name,
            description=description,
            price=price,
            discount_price=discount_price,
            discount_start=discount_start or None,
            discount_end=discount_end or None,
            stock_quantity=stock_quantity,
            stock_status=stock_status,
            category=category_instance,
            image_url=image_url,
        )

        return JsonResponse({
            "status": "success",
            "message": f"Product '{product.name}' created successfully (Custom ID: {product.custom_id})!"
        })

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Error saving product: {str(e)}"
        }, status=500)




def staff_required(user):
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(staff_required, login_url='main:home')
@csrf_exempt  # only for JS testing; remove in production if not needed
def delete_product(request, custom_id):
    if request.method != "POST":
        return JsonResponse(
            {"status": "error", "message": "Invalid request method."},
            status=405
        )

    try:
        product = get_object_or_404(Product, custom_id=custom_id)
        product_name = product.name  # store before deleting
        product.delete()

        return JsonResponse(
            {"status": "success", "message": f"Product '{product_name}' deleted successfully!"}
        )
    except Exception as e:
        return JsonResponse(
            {"status": "error", "message": f"Error deleting product: {str(e)}"},
            status=500
        )


# ==============================
# Admin Users List Page
# ==============================
@login_required
@user_passes_test(staff_required, login_url='main:home')
def admin_list_view(request):
    """
    Displays the list of all admin users.
    """
    User = get_user_model()
    # Filter only staff/admin users
    users = User.objects.filter(is_staff=True).order_by("id")

    context = {
        "title": "Admin List",  # for sidebar active class
        "users": users,
    }
    return render(request, "adminpanel/main/admin_list.html", context)


# ==============================
# Admin Users List Page - FIXED
# ==============================
@login_required
@user_passes_test(staff_required, login_url='main:home')
def admin_list_view(request):
    """
    Displays the list of all admin users and customers.
    """
    User = get_user_model()
    
    # Filter admin users (is_staff=True) - only active users
    admin_users = User.objects.filter(is_staff=True, is_active=True).order_by('-date_joined')
    
    # Filter regular customers (is_staff=False) - only active users
    customer_users = User.objects.filter(is_staff=False, is_active=True).order_by('-date_joined')

    # DEBUG: Print to console
    print(f"Found {admin_users.count()} admins")
    print(f"Found {customer_users.count()} customers")
    
    context = {
        "title": "Admin List",
        "admin_users": admin_users,
        "customer_users": customer_users,
    }
    return render(request, "adminpanel/main/admin_list.html", context)


# ==============================
# Delete Admin User
# ==============================
@login_required
@user_passes_test(staff_required, login_url='main:home')
@csrf_exempt
def delete_admin_user(request, user_id):
    """
    Deletes an admin user (staff) by ID.
    Prevents deleting yourself or superusers.
    """
    if request.method != "POST":
        return JsonResponse(
            {"status": "error", "message": "Invalid request method."},
            status=405
        )
    
    try:
        User = get_user_model()
        user = get_object_or_404(User, id=user_id)
        
        # Prevent deleting yourself
        if user.id == request.user.id:
            return JsonResponse(
                {"status": "error", "message": "You cannot delete your own account."},
                status=400
            )
        
        # Prevent deleting superusers
        if user.is_superuser:
            return JsonResponse(
                {"status": "error", "message": "Cannot delete superuser accounts."},
                status=400
            )
        
        user_email = user.email or user.username
        user.delete()
        
        return JsonResponse(
            {"status": "success", "message": f"Admin '{user_email}' deleted successfully!"}
        )
    
    except Exception as e:
        return JsonResponse(
            {"status": "error", "message": f"Error deleting admin: {str(e)}"},
            status=500
        )


# ==============================
# Delete Customer User
# ==============================
@login_required
@user_passes_test(staff_required, login_url='main:home')
@csrf_exempt
def delete_customer_user(request, user_id):
    """
    Deletes a customer user by ID.
    """
    if request.method != "POST":
        return JsonResponse(
            {"status": "error", "message": "Invalid request method."},
            status=405
        )
    
    try:
        User = get_user_model()
        user = get_object_or_404(User, id=user_id, is_staff=False)
        
        user_email = user.email or user.username
        user.delete()
        
        return JsonResponse(
            {"status": "success", "message": f"Customer '{user_email}' deleted successfully!"}
        )
    
    except Exception as e:
        return JsonResponse(
            {"status": "error", "message": f"Error deleting customer: {str(e)}"},
            status=500
        )


# ==============================
# Promote Customer to Admin
# ==============================
@login_required
@user_passes_test(staff_required, login_url='main:home')
@csrf_exempt
def promote_to_admin(request, user_id):
    """
    Promotes a customer to admin (sets is_staff=True).
    """
    if request.method != "POST":
        return JsonResponse(
            {"status": "error", "message": "Invalid request method."},
            status=405
        )
    
    try:
        User = get_user_model()
        user = get_object_or_404(User, id=user_id, is_staff=False)
        
        user.is_staff = True
        user.save()
        
        user_email = user.email or user.username
        return JsonResponse(
            {"status": "success", "message": f"Customer '{user_email}' promoted to admin successfully!"}
        )
    
    except Exception as e:
        return JsonResponse(
            {"status": "error", "message": f"Error promoting user: {str(e)}"},
            status=500
        )
        

# =============================
# Reports - FIXED VERSION
# =============================

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Sum, F, FloatField
from django.utils import timezone
from datetime import datetime, timedelta

@login_required
@user_passes_test(staff_required, login_url='main:home')
def reports(request):
    context = {
        'title': 'Reports',
    }
    return render(request, 'adminpanel/main/reports.html', context)

# API endpoints to fetch data
@login_required
@user_passes_test(staff_required, login_url='main:home')
def get_suppliers_api(request):
    """Returns static supplier data matching the suppliers page"""
    # This matches the STATIC_SUPPLIERS in reports.html
    suppliers = [
        {'name': 'Kyle Trinidad', 'email': 'kyle.trinidad@supplyco.com', 'phone': '+63-912-123-4567'},
        {'name': 'Chris Trinidad', 'email': 'chris.trinidad@freshharvest.com', 'phone': '+63-917-456-7890'},
        {'name': 'Andre Leon', 'email': 'andre.leon@veggiehub.com', 'phone': '+63-918-234-5678'},
        {'name': 'Christian Bautista', 'email': 'christian.bautista@agrosupply.com', 'phone': '+63-915-456-3210'},
        {'name': 'Patrick Navarro', 'email': 'patrick.navarro@greengrowers.com', 'phone': '+63-910-222-3344'},
        {'name': 'Joseph Cruz', 'email': 'joseph.cruz@farmfresh.com', 'phone': '+63-927-987-6543'},
    ]
    
    return JsonResponse(list(suppliers), safe=False)

@login_required
@user_passes_test(staff_required, login_url='main:home')
def get_products_api(request):
    """Returns products with their suppliers - static data matching your suppliers page"""
    products = [
        # Kyle Trinidad - Eggs
        {'product': 'White Egg', 'supplier': 'Kyle Trinidad'},
        {'product': 'Red Egg', 'supplier': 'Kyle Trinidad'},
        {'product': 'Quail Egg', 'supplier': 'Kyle Trinidad'},
        
        # Chris Trinidad - Fruits
        {'product': 'Lakatan Banana (1 bunch)', 'supplier': 'Chris Trinidad'},
        {'product': 'Melon (1pc)', 'supplier': 'Chris Trinidad'},
        {'product': 'Watermelon (500g)', 'supplier': 'Chris Trinidad'},
        {'product': 'Apple Red Fuji (per pc)', 'supplier': 'Chris Trinidad'},
        {'product': 'Papaya (1kg)', 'supplier': 'Chris Trinidad'},
        {'product': 'Grapes (200g)', 'supplier': 'Chris Trinidad'},
        {'product': 'Durian (350g)', 'supplier': 'Chris Trinidad'},
        {'product': 'Ponkan (1kg)', 'supplier': 'Chris Trinidad'},
        {'product': 'Avocado (500g)', 'supplier': 'Chris Trinidad'},
        {'product': 'Rambutan (1kg)', 'supplier': 'Chris Trinidad'},
        {'product': 'Indian Mango (1kg)', 'supplier': 'Chris Trinidad'},
        {'product': 'Pinya (1pc)', 'supplier': 'Chris Trinidad'},
        {'product': 'Pakwan (500g)', 'supplier': 'Chris Trinidad'},
        
        # Andre Leon - Vegetables
        {'product': 'Carrots (250g)', 'supplier': 'Andre Leon'},
        {'product': 'Cabbage (500g)', 'supplier': 'Andre Leon'}, 
        {'product': 'Baguio Beans (100g)', 'supplier': 'Andre Leon'},
        {'product': 'Sitaw (100g)', 'supplier': 'Andre Leon'},
        {'product': 'Ampalaya (250g)', 'supplier': 'Andre Leon'},
        {'product': 'Kamatis (350g)', 'supplier': 'Andre Leon'},
        {'product': 'Sayote (600g)', 'supplier': 'Andre Leon'},
        {'product': 'Talong (500g)', 'supplier': 'Andre Leon'},
        {'product': 'Kangkong (500g)', 'supplier': 'Andre Leon'},
        
        # Christian Bautista
        {'product': 'Cucumber (250g)', 'supplier': 'Christian Bautista'},
        {'product': 'Singkamas (250g)', 'supplier': 'Christian Bautista'},
        {'product': 'Tanglad (per bundle)', 'supplier': 'Christian Bautista'},
        {'product': 'Upo (500g)', 'supplier': 'Christian Bautista'},
        {'product': 'Patola (per pc)', 'supplier': 'Christian Bautista'},
        {'product': 'Kundol (1kg)', 'supplier': 'Christian Bautista'},
        {'product': 'Labanos (150g)', 'supplier': 'Christian Bautista'},
        
        # Patrick Navarro
        {'product': 'Malunggay (per bundle)', 'supplier': 'Patrick Navarro'},
        {'product': 'Munggo (per pack)', 'supplier': 'Patrick Navarro'},
        {'product': 'Itlog na maalat (1 dozen)', 'supplier': 'Patrick Navarro'},
        {'product': 'Mani with Shell (per pack)', 'supplier': 'Patrick Navarro'},
        {'product': 'Mani - Adobo (500g)', 'supplier': 'Patrick Navarro'},
        
        # Joseph Cruz
        {'product': 'Longan (500g)', 'supplier': 'Joseph Cruz'},
        {'product': 'Cauliflower (200g)', 'supplier': 'Joseph Cruz'},
        {'product': 'Red Bell Pepper (250g)', 'supplier': 'Joseph Cruz'},
        {'product': 'Sibuyas (400g)', 'supplier': 'Joseph Cruz'},
        {'product': 'Bawang (300g)', 'supplier': 'Joseph Cruz'},
        {'product': 'Siling Labuyo (100g)', 'supplier': 'Joseph Cruz'},
        {'product': 'Kalabasa (1pc)', 'supplier': 'Joseph Cruz'},
        {'product': 'Kalabasa (1kg)', 'supplier': 'Joseph Cruz'},
        {'product': 'Kamote Yellow (500g)', 'supplier': 'Joseph Cruz'},
        {'product': 'Kamote Violet (500g)', 'supplier': 'Joseph Cruz'},
        {'product': 'Gabi (250g)', 'supplier': 'Joseph Cruz'},
        {'product': 'Luya (250g)', 'supplier': 'Joseph Cruz'},
    ]
    
    return JsonResponse(list(products), safe=False)

@login_required
@user_passes_test(staff_required, login_url='main:home')
def get_statistics_api(request):
    """Calculate fast and slow moving products based on actual sales data"""
    from main.models import OrderItem, Product  # Import your models
    
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    
    # Convert string dates to datetime objects
    if start_date and end_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            # Make them timezone aware
            start_dt = timezone.make_aware(start_dt) if timezone.is_naive(start_dt) else start_dt
            end_dt = timezone.make_aware(end_dt) if timezone.is_naive(end_dt) else end_dt
        except ValueError:
            # If date parsing fails, use default
            end_dt = timezone.now()
            start_dt = end_dt - timedelta(days=30)
    else:
        # Default to last 30 days
        end_dt = timezone.now()
        start_dt = end_dt - timedelta(days=30)
    
    # Get product sales within date range
    product_sales = OrderItem.objects.filter(
        order__created_at__gte=start_dt,
        order__created_at__lte=end_dt,
        order__status__in=['completed', 'shipped', 'delivered']
    ).values(
        'product__name'
    ).annotate(
        sold=Sum('quantity'),
        total=Sum(F('quantity') * F('price_at_purchase'), output_field=FloatField())
    ).order_by('-sold')
    
    # Get fast moving (top 5 or more)
    fast_moving = []
    for item in product_sales[:10]:  # Get top 10 to show more data
        try:
            product = Product.objects.get(name=item['product__name'])
            fast_moving.append({
                'product': item['product__name'],
                'sold': int(item['sold']),
                'unitPrice': float(product.price),
                'total': float(item['total']) if item['total'] else 0
            })
        except Product.DoesNotExist:
            continue
    
    # Get slow moving (bottom products with at least 1 sale)
    slow_moving = []
    if product_sales.count() > 10:
        slow_items = list(product_sales.order_by('sold')[:10])
        for item in slow_items:
            try:
                product = Product.objects.get(name=item['product__name'])
                slow_moving.append({
                    'product': item['product__name'],
                    'sold': int(item['sold']),
                    'unitPrice': float(product.price),
                    'total': float(item['total']) if item['total'] else 0
                })
            except Product.DoesNotExist:
                continue
    
    statistics = {
        'fast': fast_moving,
        'slow': slow_moving
    }
    
    return JsonResponse(statistics)

# =============================
# Suppliers List
# =============================

def supplier_list(request):
    context = {
        'title': 'Supplier List',
    }
    return render(request, "adminpanel/main/suppliers.html", context)