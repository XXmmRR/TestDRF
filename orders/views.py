from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import Order
from .serializers import OrderSerializer, AdminOrderSerializer
from drf_spectacular.utils import extend_schema


@extend_schema(tags=["Orders"])
class OrderViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["status"]
    ordering_fields = ["created_at", "total_price"]

    def get_queryset(self):
        user = self.request.user
        queryset = (
            Order.objects.all()
            .select_related("user")
            .prefetch_related("items__product")
        )

        # ДЛЯ DRF-SPECTACULAR
        if getattr(self, "swagger_fake_view", False):
            return queryset.all() 

        if user.is_staff:
            return queryset

        return queryset.filter(user=user)
    def get_serializer_class(self):
        if self.action in ["set_status", "update", "partial_update"] and self.request.user.is_staff:
            return AdminOrderSerializer
        return OrderSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["patch"], permission_classes=[IsAdminUser])
    def set_status(self, request, pk=None):
        order = self.get_object()
        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"status": f"Статус заказа #{order.id} изменен на '{order.status}'."}
        )

    def get_permissions(self):
        if self.action in ["set_status", "update", "partial_update", "destroy"]:
            self.permission_classes = [IsAdminUser]
        elif self.action in ["create", "list", "retrieve"]:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()