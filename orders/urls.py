from django.urls import path

from . import views

urlpatterns = [
    path("", views.place_order, name="place_order"),
    path("payments/", views.payment, name="payment"),
    path("payments/sslc/status", views.payment_status, name="payment_status"),
    path(
        "payments/sslc/complete/<val_id>/<tran_id>/",
        views.sslc_complete,
        name="sslc_complete",
    ),
]
