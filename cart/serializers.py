from rest_framework import serializers
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.IntegerField(source='product.id')
    product_name = serializers.CharField(
        source='product.name',
        read_only=True
    )

    subtotal = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = CartItem
        fields = [
            'id',
            'product',
            'product_name',
            'quantity',
            'subtotal',
        ]


class CartSerializer(serializers.ModelSerializer):

    items = CartItemSerializer(
        many=True,
        read_only=True
    )

    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            'id',
            'user',
            'session_key',
            'created_at',
            'items',
            'total',
        ]

    read_only_fields = [
        'user',
        'session_key',
        'created_at',
        'items',
        'total',
    ]

    def get_total(self, obj):
        return sum(
            item.subtotal
            for item in obj.items.all()
        )
