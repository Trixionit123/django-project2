from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Order, OrderItem
from products.models import Product


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-id')
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_create(request):
    if request.method == 'POST':
        product_id = request.POST.get('product')
        quantity = int(request.POST.get('quantity', '1') or '1')
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            messages.error(request, 'Товар не найден')
            return redirect('order_create')
        order = Order.objects.create(user=request.user)
        OrderItem.objects.create(order=order, product=product, quantity=quantity, price=product.price)
        order.total_price = sum(i.price * i.quantity for i in order.items.all())
        order.save()
        messages.success(request, 'Заказ создан')
        return redirect('order_list')

    products = Product.objects.all().order_by('name')
    return render(request, 'orders/order_create.html', {'products': products})


