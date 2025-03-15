import datetime

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from carts.models import CartItem
from products.models import Product

from .models import Order, OrderProduct
from .utils import send_order_confirmation_email


@csrf_exempt
@login_required
def place_order(request, total=0, quantity=0,):
    current_user = request.user

    cart_items = CartItem.objects.filter(user=current_user).select_related("product")
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('home')
    
    grand_total = 0
    total = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    grand_total = float(total) + float(6.90)
    
    
    if request.method == 'POST':
        payment_option = request.POST.get('flexRadioDefault', 'cash')
        
        try:
            current_date = datetime.date.today()
            order_number = current_date.strftime("%Y%m%d") + str(cart_count)
            
            order = Order.objects.create(
                user=current_user,
                mobile=current_user.mobile,
                email=current_user.email,
                address_line_1=current_user.address_line_1,
                address_line_2=current_user.address_line_2,
                country=current_user.country,
                state=current_user.state,
                city=current_user.city,
                order_note=request.POST.get('order_note', ''),
                order_total=grand_total,
                status='New',
                order_number=order_number,
            )

            for cart_item in cart_items:
                OrderProduct.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    product_price=cart_item.product.price,
                    user=current_user, 
                )

                product = Product.objects.get(id=cart_item.product.id)
                if product.stock >= cart_item.quantity:
                    product.stock -= cart_item.quantity
                    product.save()
                else:
                    return HttpResponse("Not enough stock available for product: {}".format(product.name))
                
                cart_item.delete()
            
            send_order_confirmation_email(current_user, order)
            
            if payment_option == 'cash':
                return redirect('order_complete')
            elif payment_option == 'sslcommerz':
                return redirect("payment")
            
        except Exception as e:
            return HttpResponse('Error occurred: ' + str(e))
    
    context = {
        'user':current_user,
        'cart_items': cart_items,
        'grand_total': grand_total,
        'total': total,
    }
    return render(request, 'orders/checkout.html', context)
