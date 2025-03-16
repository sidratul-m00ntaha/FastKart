from django.db import models
from django.db.models import Avg, Count
from django.utils.text import slugify

from accounts.models import CustomUser


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-managed "created_at" and
    "updated_at" fields.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    category_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    category_image = models.ImageField(upload_to="categories")

    def save(self, *args, **kwargs):
        self.slug = slugify(self.category_name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.category_name


class Product(TimeStampedModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00
    )
    stock = models.PositiveIntegerField()
    available = models.BooleanField(default=True)
    unit = models.CharField(max_length=100, null=True, blank=True)
    rating = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, null=True, blank=True
    )

    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.CASCADE
    )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def discount_price(self):
        return self.price * (1 - self.discount_percentage / 100)

    @property
    def savings(self):
        """Calculate the savings by subtracting the discount price from the original price."""
        return self.price - self.discount_price

    def get_discounted_price(self):
        if self.discount_price:
            return self.discount_price
        return self.price

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.name

    def averageReview(self):
        reviews = Review.objects.filter(product=self, status=True).aggregate(
            average=Avg("rating")
        )
        avg = 0
        if reviews["average"] is not None:
            avg = float(reviews["average"])
        self.rating = avg
        return avg

    def count_review(self):
        reviews = Review.objects.filter(product=self, status=True).aggregate(
            count=Count("id")
        )
        count = 0
        if reviews["count"] is not None:
            count = int(reviews["count"])
        return count


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="products/images")

    def __str__(self):
        return f"Image for {self.product.name}"


class Review(TimeStampedModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user")
    rating = models.FloatField()
    review = models.TextField(max_length=500, blank=True)

    status = models.BooleanField(default=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"
