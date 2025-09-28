from django.db import models
from accounts.models import User
from products.models import Product

class Order(models.Model):
    STATUS_CHOICES = (
        ('new', 'Новый'),
        ('in_progress', 'В обработке'),
        ('completed', 'Выполнен'),
        ('cancelled', 'Отменен'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name="Пользователь")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Общая стоимость")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ #{self.pk} от {self.user.email}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена на момент заказа")

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"
        unique_together = ('order', 'product')

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"