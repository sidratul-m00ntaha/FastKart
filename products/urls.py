from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path(
        "categories/<slug:category_slug>/products",
        views.category_products,
        name="category_products",
    ),
    path("products/<slug:product_slug>/", views.product_detail, name="product_detail"),
    path(
        "products/<slug:product_slug>/review/",
        views.submit_review,
        name="submit_review",
    ),
]
