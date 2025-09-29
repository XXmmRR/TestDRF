from rest_framework import serializers
from .models import Order, OrderItem
from products.models import Product


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = OrderItem
        fields = ["product", "quantity"]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Количество товара должно быть больше 0.")
        return value


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "user", "status", "created_at", "items", "total_price"]
        read_only_fields = ["user", "status", "created_at", "total_price"]

    def create(self, validated_data):
        items_data = validated_data.pop("items")

        # Создаем сам заказ без позиций
        order = Order.objects.create(**validated_data)

        total_price = 0

        for item_data in items_data:
            product = item_data["product"]
            quantity = item_data["quantity"]

            if product.stock < quantity:
                order.delete()
                raise serializers.ValidationError(
                    f"На складе недостаточно товара: {product.name}."
                )

            product.stock -= quantity
            product.save()

            OrderItem.objects.create(
                order=order, product=product, quantity=quantity, price=product.price
            )
            total_price += product.price * quantity

        order.total_price = total_price
        order.save()

        return order


class AdminOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["status"]
