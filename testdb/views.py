from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model

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
    print("🟡 register_view called")
    context = {}

    if request.method == "POST":
        print("🟢 POST request received")

        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        # Field-level validation
        if not username:
            context["username_error"] = "Username is required."
        if not email:
            context["email_error"] = "Email is required."
        if not password:
            context["password_error"] = "Password is required."
        if not confirm_password:
            context["confirm_password_error"] = "Please confirm your password."
        if password and confirm_password and password != confirm_password:
            context["confirm_password_error"] = "Passwords do not match."

        # Check for existing username/email
        if username and User.objects.filter(username=username).exists():
            context["username_error"] = "This username is already taken."

        if email and User.objects.filter(email=email).exists():
            context["email_error"] = "This email is already registered."

        # If any errors, show modal and return
        if any(context.get(key) for key in context):
            context["show_login_modal"] = True  # Modal should open
            return render(request, "main/home.html", context)

        # Create new user
        new_user = User.objects.create_user(username=username, email=email, password=password)
        login(request, new_user)
        print(f"🟢 Registration successful for user {new_user.username}")
        return redirect("home")  # Redirect to home or profile

    return redirect("home")  # Or render a registration page directly
