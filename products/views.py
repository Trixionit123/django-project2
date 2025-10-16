from rest_framework import generics, permissions
from .models import Product
from .serializers import ProductSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET',):
            return True
        return bool(request.user and request.user.is_staff)


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all().order_by('-id')
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]


class ProductRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]


