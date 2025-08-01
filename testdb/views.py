from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.contrib.auth.models import User
import re

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

        # ✅ USERNAME VALIDATION
        if not username:
            context["username_error"] = "Please enter a username."
        elif len(username) < 3:
            context["username_error"] = "Username must be at least 3 characters long."
        elif not re.match(r"^[A-Za-z0-9_.-]+$", username):
            context["username_error"] = "Username can only use letters, numbers, underscores (_), dashes (-), and dots (.)"
        elif User.objects.filter(username=username).exists():
            context["username_error"] = "This username is already taken. Try another one."

        # ✅ EMAIL VALIDATION
        if not email:
            context["email_error"] = "Please enter an email address."
        elif not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
            context["email_error"] = "Please enter a valid email address (e.g. you@example.com)."
        elif User.objects.filter(email=email).exists():
            context["email_error"] = "This email is already registered. Try logging in instead."

        # ✅ PASSWORD VALIDATION
        if not password:
            context["password_error"] = "Please create a password."
        elif len(password) < 6:
            context["password_error"] = "Password must be at least 6 characters long."
        elif not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
            context["password_error"] = "Password must contain both letters and numbers."

        # ✅ CONFIRM PASSWORD CHECK
        if not confirm_password:
            context["confirm_password_error"] = "Please confirm your password."
        elif password != confirm_password:
            context["confirm_password_error"] = "Passwords do not match."

        # If any errors exist, return with feedback
        if context:
            context.update({
                "show_login_modal": True,
                "register_mode": True,
                "form_data": {
                    "username": username,
                    "email": email
                }
            })
            return render(request, "main/home.html", context)

        # ✅ Create the user if all validations pass
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            return redirect("home")
        except Exception as e:
            print("🔴 Exception while creating user:", e)

            context.update({
                "registration_error": "Something went wrong on our end. Please try again shortly.",
                "show_login_modal": True,
                "register_mode": True,
                "form_data": {
                    "username": username,
                    "email": email
                }
            })
            return render(request, 'main/home.html', context)

    return redirect("home")


def home_view(request):
    context = {}
    if "form_errors" in request.session:
        context.update(request.session.pop("form_errors"))
    return render(request, "main/home.html", context)
