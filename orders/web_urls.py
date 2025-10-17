from django.urls import path
from . import web_views


urlpatterns = [
    path('orders/', web_views.order_list, name='order_list'),
    path('orders/create/', web_views.order_create, name='order_create'),
]


