from django.urls import path
from . import views


urlpatterns = [
    path('', views.ProductListCreateView.as_view(), name='product-list-create'),
    path('<int:pk>/', views.ProductRetrieveUpdateDeleteView.as_view(), name='product-detail'),
]


