from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render

from products.models import Product

from .models import Cart, CartProduct
from .utils import get_session_key


def add_cart(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    try:
        cart = Cart.objects.get(session_key=get_session_key(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            session_key=get_session_key(request), user=request.user
        )

    try:
        cart_product = CartProduct.objects.get(product=product, cart=cart)
    except CartProduct.DoesNotExist:
        cart_product = CartProduct(
            product=product,
            cart=cart,
            quantity=0,
        )

    cart_product.quantity += 1
    cart_product.save()

    url = request.META.get("HTTP_REFERER")
    return redirect(url)


def remove_cart(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    if request.user.is_authenticated:
        cart = get_object_or_404(Cart, user=request.user)
    else:
        cart = get_object_or_404(Cart, session_key=get_session_key(request))

    cart_product = get_object_or_404(CartProduct, product=product, cart=cart)
    if cart_product.quantity > 1:
        cart_product.quantity -= 1
        cart_product.save()
    else:
        cart_product.delete()

    url = request.META.get("HTTP_REFERER")
    return redirect(url)


def cart_detail(request, total=0, quantity=0, cart_products=None):
    if request.user.is_authenticated:
        cart = get_object_or_404(Cart, user=request.user)
    else:
        cart = get_object_or_404(Cart, session_key=get_session_key(request))

    cart_products = CartProduct.objects.filter(cart=cart).select_related("product")
    total = 0
    for cart_product in cart_products:
        total += cart_product.product.price * cart_product.quantity
        quantity += cart_product.quantity

    context = {
        "total": total,
        "quantity": quantity,
        "cart_items": cart_products,
        "grand_total": total + settings.DELIVERY_CHARGE,
    }
    return render(request, "carts/cart.html", context)
