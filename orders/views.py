from rest_framework import generics, permissions
from .models import Order
from .serializers import OrderSerializer
from .tasks import send_order_confirmation, publish_order_event
from django.utils import timezone
from myproject.kafka_utils import publish_order_created


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        order = serializer.save(user=self.request.user)
        user = self.request.user
        if getattr(user, 'email', None):
            send_order_confirmation.delay(order.id, user.email)
        # publish kafka event via Celery
        publish_order_event.delay({
            'type': 'order.created',
            'order_id': order.id,
            'user_id': user.id,
            'total_price': str(order.total_price),
            'status': order.status,
            'created_at': timezone.now().isoformat(),
        })


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-id')


class OrderDetailView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class OrderStatusUpdateView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAdmin]


