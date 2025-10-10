from rest_framework import serializers
from decimal import Decimal
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, required=False)

    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'status', 'total_price', 'items']
        read_only_fields = ['user', 'created_at', 'total_price']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        order = Order.objects.create(**validated_data)
        total = Decimal('0')
        for item in items_data:
            order_item = OrderItem.objects.create(order=order, **item)
            total += (Decimal(order_item.price) * order_item.quantity)
        order.total_price = total
        order.save()
        return order


