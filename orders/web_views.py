from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from decimal import Decimal
from .models import Order, OrderItem
from products.models import Product
from .tasks import send_order_confirmation, publish_order_event
from django.utils import timezone
from myproject.kafka_utils import publish_order_created


class OrderListView(LoginRequiredMixin, View):
    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-id')
        return render(request, 'orders/order_list.html', {'orders': orders})


class OrderCreateView(LoginRequiredMixin, View):
    def get(self, request):
        products = Product.objects.all().order_by('name')
        return render(request, 'orders/order_create.html', {'products': products})

    def post(self, request):
        product_id = request.POST.get('product')
        quantity_raw = request.POST.get('quantity', '1')
        try:
            quantity = int(quantity_raw)
        except (TypeError, ValueError):
            quantity = 1

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            messages.error(request, 'Товар не найден')
            return redirect('order_create')

        order = Order.objects.create(user=request.user)
        OrderItem.objects.create(order=order, product=product, quantity=quantity, price=product.price)
        # Ensure Decimal-safe total calculation
        total = sum((Decimal(item.price) * item.quantity) for item in order.items.all())
        order.total_price = total
        order.save()
        if request.user.email:
            send_order_confirmation.delay(order.id, request.user.email)
        # publish kafka event via Celery
        publish_order_event.delay({
            'type': 'order.created',
            'order_id': order.id,
            'user_id': request.user.id,
            'total_price': str(order.total_price),
            'status': order.status,
            'created_at': timezone.now().isoformat(),
        })
        messages.success(request, 'Заказ создан')
        return redirect('order_list')


