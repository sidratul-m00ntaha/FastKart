from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Product, ProductImage, Review

admin.site.register([Category, ProductImage, Review])


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />',
                obj.image.url,
            )
        return "(No image)"

    readonly_fields = ("image_preview",)
    fields = ("image_preview", "image")
    verbose_name_plural = "Product Images"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
