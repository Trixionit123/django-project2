from django.urls import path
from .web_views import OrderListView, OrderCreateView


urlpatterns = [
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('orders/create/', OrderCreateView.as_view(), name='order_create'),
]


