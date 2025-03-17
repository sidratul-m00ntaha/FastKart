from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render

from products.models import Product

from .models import Cart, CartItem
from .utils import get_session_key


def add_cart(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    try:
        cart = Cart.objects.get(session_key=get_session_key(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(session_key=get_session_key(request))

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
    except CartItem.DoesNotExist:
        cart_item = CartItem(
            product=product,
            cart=cart,
            user=request.user,
            quantity=0,
        )

    cart_item.quantity += 1
    cart_item.save()

    url = request.META.get("HTTP_REFERER")
    return redirect(url)


def remove_cart(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    if request.user.is_authenticated:
        cart = get_object_or_404(Cart, user=request.user)
    else:
        cart = get_object_or_404(Cart, session_key=get_session_key(request))

    cart_item = get_object_or_404(CartItem, product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    url = request.META.get("HTTP_REFERER")
    return redirect(url)


def cart_detail(request, total=0, quantity=0, cart_items=None):
    if request.user.is_authenticated:
        cart = get_object_or_404(Cart, user=request.user)
    else:
        cart = get_object_or_404(Cart, session_key=get_session_key(request))

    cart_items = CartItem.objects.filter(cart=cart).select_related("product")
    total = 0
    for cart_item in cart_items:
        total += cart_item.product.discount_price * cart_item.quantity
        quantity += cart_item.quantity

    context = {
        "total": total,
        "quantity": quantity,
        "cart_items": cart_items,
        "grand_total": total + settings.DELIVERY_CHARGE,
    }
    return render(request, "carts/cart.html", context)
