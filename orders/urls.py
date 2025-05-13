from django.urls import path

from . import views

urlpatterns = [
    path("", views.place_order, name="place_order"),
    path("payment/", views.payment, name="payment"),
    path("payment/status", views.payment_status, name="payment_status"),
]
