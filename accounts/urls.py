from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views

urlpatterns = [
    path('signup/', views.user_signup, name='signup'),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path('profile/', views.user_dashboard, name='profile'),
    path('verify/<uidb64>/<token>/', views.verify_email, name='verify-email'),
]