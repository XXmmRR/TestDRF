from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from .models import Product
from .serializers import ProductSerializer

from drf_spectacular.utils import extend_schema


@extend_schema(tags=['Products'])
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]