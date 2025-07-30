from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model

User = get_user_model()

def login_view(request):
    print("🟡 login_view called")  # Add this line
    if request.method == "POST":
        print("🟢 POST request received")
        identifier = request.POST.get("identifier")
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=identifier)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=identifier)
            except User.DoesNotExist:
                print("DEBUG: No user found with that username or email")
                return render(request, "main/home.html", {
                    "login_error": "User not found."
                })

        authenticated_user = authenticate(request, username=user.username, password=password)

        if authenticated_user is not None:
            login(request, authenticated_user)
            print(f"DEBUG: Login successful for user {authenticated_user.username}")
            return redirect("home")  # or wherever your homepage is
        else:
            print("DEBUG: Password incorrect")
            return render(request, "main/home.html", {
                "login_error": "Incorrect password."
            })

    return render(request, "main/home.html")
