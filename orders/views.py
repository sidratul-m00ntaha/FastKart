import datetime
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from sslcommerz_python_api import SSLCSession

from carts.models import Cart, CartItem
from carts.utils import get_session_key
from products.models import Product

from .models import Order, OrderProduct, Payment
from .utils import send_order_confirmation_email


@csrf_exempt
@login_required
def place_order(
    request,
    total=0,
    quantity=0,
):
    current_user = request.user

    cart = get_object_or_404(Cart, session_key=get_session_key(request))
    cart_items = CartItem.objects.filter(cart=cart).select_related("product")
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect("home")

    grand_total = 0
    total = 0
    for cart_item in cart_items:
        total += cart_item.product.price * cart_item.quantity
        quantity += cart_item.quantity
    grand_total = float(total) + settings.DELIVERY_CHARGE

    if request.method == "POST":
        payment_option = request.POST.get("flexRadioDefault", "cash")  # sslcommercez

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
                postcode=current_user.postcode,
                city=current_user.city,
                order_note=request.POST.get("order_note", ""),
                order_total=grand_total,
                status="New",
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
                    return HttpResponse(
                        "Not enough stock available for product: {}".format(
                            product.name
                        )
                    )

                cart_item.delete()

            send_order_confirmation_email(current_user, order)

            if payment_option == "cash":
                return redirect("order_complete")
            elif payment_option == "sslcommerz":
                return redirect("payment")

        except Exception as e:
            return HttpResponse("Error occurred: " + str(e))

    context = {
        "user": current_user,
        "cart_items": cart_items,
        "grand_total": grand_total,
        "total": total,
    }
    return render(request, "orders/checkout.html", context)


@login_required
def payment(request):
    mypayment = SSLCSession(
        sslc_is_sandbox=settings.SSLCOMMERZ_IS_SANDBOX,
        sslc_store_id=settings.SSLCOMMERZ_STORE_ID,
        sslc_store_pass=settings.SSLCOMMERZ_STORE_PASS,
    )

    status_url = request.build_absolute_uri("sslc/status")

    mypayment.set_urls(
        success_url=status_url,
        fail_url=status_url,
        cancel_url=status_url,
        ipn_url=status_url,
    )

    user = request.user
    order = Order.objects.filter(user=user, is_ordered=False).last()

    mypayment.set_product_integration(
        total_amount=Decimal(order.order_total),
        currency="BDT",
        product_category="clothing",
        product_name="demo-product",
        num_of_item=2,
        shipping_method="YES",
        product_profile="None",
    )

    mypayment.set_customer_info(
        name=user.username,
        email=user.email,
        address1=user.address_line_1,
        address2=user.address_line_1,
        city=user.city,
        postcode=user.postcode,
        country=user.country,
        phone=user.mobile,
    )

    mypayment.set_shipping_info(
        shipping_to=user.get_full_name(),
        address=user.full_address(),
        city=user.city,
        postcode=user.postcode,
        country=user.country,
    )

    response_data = mypayment.init_payment()
    return redirect(response_data["GatewayPageURL"])


@csrf_exempt
def payment_status(request):
    if request.method == "POST":
        payment_data = request.POST
        if payment_data["status"] == "VALID":
            val_id = payment_data["val_id"]
            tran_id = payment_data["tran_id"]

            return HttpResponseRedirect(
                reverse("sslc_complete", kwargs={"val_id": val_id, "tran_id": tran_id})
            )
        else:
            return JsonResponse({"status": "error", "message": "Payment failed"})

    return render(request, "orders/status.html")


def sslc_complete(request, val_id, tran_id):
    try:
        order = Order.objects.filter(user=request.user, is_ordered=False).last()

        payment = Payment.objects.create(
            user=request.user,
            payment_id=val_id,
            payment_method="SSLCommerz",
            amount_paid=order.order_total,
            status="Completed",
        )

        order.is_ordered = True
        order.status = "Completed"
        order.payment = payment
        order.save()

        # CartItems will be automatically deleted
        Cart.objects.filter(user=request.user).delete()

        context = {
            "order": order,
            "transaction_id": tran_id,
        }
        return render(request, "orders/status.html", context)

    except Order.DoesNotExist:
        return HttpResponse("Order not found", status=404)
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}", status=500)
