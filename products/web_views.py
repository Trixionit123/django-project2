from django.shortcuts import render, get_object_or_404
from .models import Product


def product_list(request):
    products = Product.objects.select_related('category').all().order_by('-id')
    return render(request, 'products/product_list.html', {'products': products})


def product_detail(request, pk: int):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/product_detail.html', {'product': product})


