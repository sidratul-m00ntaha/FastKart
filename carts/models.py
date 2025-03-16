from django.db import models

from accounts.models import CustomUser
from products.models import Product, TimeStampedModel


class Cart(TimeStampedModel):
    session_key = models.CharField(max_length=250)
    user = models.ForeignKey(CustomUser, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.session_key


class CartItem(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, null=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=0)

    def sub_total(self):
        return self.product.discount_price * self.quantity

    def __str__(self):
        return f"CartItem: {self.product.name}"
