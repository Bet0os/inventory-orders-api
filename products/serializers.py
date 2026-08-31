from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError

from .models import (
    Product,
    Category,
    Supplier,
    InventoryMovement
)


# ==================================================
# PRODUCT
# ==================================================

class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'


# ==================================================
# CATEGORY
# ==================================================

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = '__all__'


# ==================================================
# SUPPLIER
# ==================================================

class SupplierSerializer(serializers.ModelSerializer):

    class Meta:
        model = Supplier
        fields = '__all__'


# ==================================================
# INVENTORY MOVEMENT
# ==================================================

class InventoryMovementSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        try:
            return super().create(validated_data)

        except DjangoValidationError as error:
            raise serializers.ValidationError(
                error.message_dict
            )

    def update(self, instance, validated_data):
        try:
            return super().update(
                instance,
                validated_data
            )

        except DjangoValidationError as error:
            raise serializers.ValidationError(
                error.message_dict
            )

    class Meta:
        model = InventoryMovement
        fields = '__all__'


class InventoryHistorySerializer(serializers.ModelSerializer):

    product = ProductSerializer(
        read_only=True
    )

    supplier = SupplierSerializer(
        read_only=True
    )

    class Meta:
        model = InventoryMovement
        fields = [
            'id',
            'movement_type',
            'reason',
            'quantity',
            'created_at',
            'product',
            'supplier',
            'order_item'
        ]
