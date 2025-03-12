from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm

from accounts.models import CustomUser
from accounts.forms import CustomUserRegistrationForm
from accounts.utils import send_verification_email


def user_signup(request):
    if request.method == "POST":
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_verification_email(request, user)
            login(request, user)
            return redirect("profile")
    else:
        form = CustomUserRegistrationForm()
    
    return render(request, 'accounts/signup.html')


def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have successfully logged in.")
            return redirect("profile")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, "accounts/login.html", {"form": form})


@login_required
def user_logout(request):
    logout(request)
    return redirect('signup')


@login_required
def user_dashboard(request):
    user = request.user

    if request.method == 'POST':
        user.email = request.POST.get('email', user.email)
        user.mobile = request.POST.get('mobile', user.mobile)
        user.address_line_1 = request.POST.get('address_line_1', user.address_line_1)
        user.address_line_2 = request.POST.get('address_line_2', user.address_line_2)
        user.city = request.POST.get('city', user.city)
        user.state = request.POST.get('state', user.state)
        user.country = request.POST.get('country', user.country)
        user.save()

        return redirect('profile')

    context = { 'user_info': user}
    return render(request, 'accounts/profile.html', context)


def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_verified = True
        user.save()
        messages.success(request, 'Your email has been verified successfully.')
        return redirect('login')
    else:
        messages.error(request, 'The verification link is invalid or has expired.')
        return redirect('signup')
