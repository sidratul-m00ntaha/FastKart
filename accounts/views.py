from django.shortcuts import render
from django.contrib.auth import login

from accounts.forms import CustomUserRegistrationForm


def signup(request):
    if request.method == "POST":
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # return redirect("dashboard")
    else:
        form = CustomUserRegistrationForm()
    
    return render(request, 'accounts/signup.html')
