from rest_framework import serializers

from .models import Order, OrderItem


# ==================================================
# ORDER ITEM
# ==================================================

class OrderItemSerializer(serializers.ModelSerializer):

    product_name = serializers.CharField(
        source='product.name',
        read_only=True
    )

    calculated_total = serializers.SerializerMethodField()

    def get_calculated_total(self, obj):
        return obj.price * obj.quantity

    class Meta:
        model = OrderItem

        fields = [
            'id',
            'product',
            'product_name',
            'quantity',
            'price',
            'subtotal',
            'calculated_total',
        ]


# ==================================================
# ORDER
# ==================================================

class OrderSerializer(serializers.ModelSerializer):

    items = OrderItemSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Order

        fields = [
            'id',
            'user',
            'total',
            'status',
            'shipping_address',
            'payment_method',
            'created_at',
            'items',
        ]

        read_only_fields = [
            'user',
            'total',
            'status',
            'created_at',
            'items',
        ]
