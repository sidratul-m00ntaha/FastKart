from .models import Cart, CartItem
from .utils import get_session_key
from django.db.models import Sum


def counter(request):
    if 'admin' in request.path:
        return {}
    
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(user=request.user).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    else:
        cart = Cart.objects.filter(session_key=get_session_key(request)).last()
        if cart:
            cart_count = CartItem.objects.filter(cart=cart).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    return {"cart_count": cart_count}
