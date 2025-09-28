from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import Order
from .serializers import OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at', 'total_price']

    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.all().select_related('user').prefetch_related('items__product')
        if user.is_staff:
            return queryset
        return queryset.filter(user=user)
    
    # Создаем заказ в транзакции
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser])
    def set_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        
        if new_status and new_status in [choice[0] for choice in Order.STATUS_CHOICES]:
            order.status = new_status
            order.save()
            return Response({'status': f"Статус заказа #{order.id} изменен на '{new_status}'."})
        
        return Response({'error': 'Некорректный статус'}, status=status.HTTP_400_BAD_REQUEST)
    
    def get_permissions(self):
        if self.action in ['set_status', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminUser]
        elif self.action in ['create', 'list', 'retrieve']:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()