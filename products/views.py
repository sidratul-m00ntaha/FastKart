from django.shortcuts import render
from django.db.models import Count
from .models import Product, Category


def home(request):
    products = Product.objects.all()
    categories = Category.objects.annotate(product_count=Count('products'))
    
    context={
        'products': products,
        'categories': categories
    }
    
    return render(request, 'products/home.html', context)
