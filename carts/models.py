from django.db import models
from products.models import Product, TimeStampedModel
from accounts.models import CustomUser


class Cart(TimeStampedModel):
    session_key = models.CharField(max_length=250)

    def __str__(self):
        return self.session_key


class CartItem(TimeStampedModel):
    user = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING, null=True)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, null=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=0)

    def sub_total(self):
        return self.product.discount_price * self.quantity

    def __str__(self):
        return f"CartItem: {self.product.name}"
