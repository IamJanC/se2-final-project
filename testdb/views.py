from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.http import JsonResponse

User = get_user_model()

def login_view(request):
    print("🟡 login_view called")
    context = {}

    if request.method == "POST":
        print("🟢 POST request received")

        identifier = request.POST.get("identifier")
        password = request.POST.get("password")

        # Field-level blank checks
        if not identifier:
            context["identifier_error"] = "Please enter your username or email."
        if not password:
            context["password_error"] = "Please enter your password."

        # If any field was blank, return early
        if context.get("identifier_error") or context.get("password_error"):
            context["show_login_modal"] = True
            return render(request, "main/home.html", context)

        # Attempt to get user by username or email
        try:
            user = User.objects.get(username=identifier)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=identifier)
            except User.DoesNotExist:
                print("🔴 User not found")
                context["login_error"] = "Invalid username/email or password."
                context["show_login_modal"] = True
                return render(request, "main/home.html", context)

        # Attempt authentication
        authenticated_user = authenticate(request, username=user.username, password=password)
        if authenticated_user:
            login(request, authenticated_user)
            print(f"🟢 Login successful for user {authenticated_user.username}")
            return redirect("home")
        else:
            print("🔴 Incorrect password")
            context["login_error"] = "Invalid username/email or password."
            context["show_login_modal"] = True
            return render(request, "main/home.html", context)

    return render(request, "main/home.html")

def register_view(request):
    context = {}
    
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        # Field-level blank checks
        if not username:
            context["username_error"] = "Username is required."
        if not email:
            context["email_error"] = "Email is required."
        if not password:
            context["password_error"] = "Password is required."
        if not confirm_password:
            context["confirm_password_error"] = "Please confirm your password."

        # Only check for existing username if username was provided
        if username and not context.get("username_error"):
            if User.objects.filter(username=username).exists():
                context["username_error"] = "This username is already in use."

        # Only check for existing email if email was provided
        if email and not context.get("email_error"):
            if User.objects.filter(email=email).exists():
                context["email_error"] = "This email is already registered."

        # Password match check
        if password and confirm_password and password != confirm_password:
            context["confirm_password_error"] = "Passwords do not match."

        if context:  # If any errors
            context.update({
                "show_login_modal": True,
                "register_mode": True,
                "form_data": {
                    'username': username,
                    'email': email
                }
            })
            return render(request, "main/home.html", context)

        # Create user if no errors
        try:
            new_user = User.objects.create_user(username=username, email=email, password=password)
            login(request, new_user)
            return redirect("home")
        except Exception as e:
            context.update({
                "username_error": "Registration failed. Please try again.",
                "show_login_modal": True,
                "register_mode": True,
                "form_data": {
                    'username': username,
                    'email': email
                }
            })
            return render(request, "main/home.html", context)

    return redirect("home")


def home_view(request):
    context = {}
    if "form_errors" in request.session:
        context.update(request.session.pop("form_errors"))
    return render(request, "main/home.html", context)




