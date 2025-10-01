from django.urls import path
from . import web_views


urlpatterns = [
    path('products/', web_views.product_list, name='product_list'),
    path('products/<int:pk>/', web_views.product_detail, name='product_detail'),
]


