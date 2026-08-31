from django.db import models, transaction
from django.core.exceptions import ValidationError


# ==================================================
# CATEGORY
# ==================================================

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


# ==================================================
# SUPPLIER
# ==================================================

class Supplier(models.Model):
    name = models.CharField(max_length=150)

    contact_email = models.EmailField(
        blank=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    def __str__(self):
        return self.name


# ==================================================
# PRODUCT
# ==================================================

class Product(models.Model):
    name = models.CharField(
        max_length=200
    )

    sku = models.CharField(
        max_length=50,
        unique=True
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    stock = models.PositiveIntegerField(
        default=0
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products'
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )

    def __str__(self):
        return self.name


# ==================================================
# INVENTORY MOVEMENT
# ==================================================

class InventoryMovement(models.Model):

    MOVEMENT_TYPES = [
        ('IN', 'Entrada'),
        ('OUT', 'Salida'),
    ]

    REASON_CHOICES = [
        ('PURCHASE', 'Compra'),
        ('SALE', 'Venta'),
        ('ADJUSTMENT', 'Ajuste'),
    ]

    movement_type = models.CharField(
        max_length=3,
        choices=MOVEMENT_TYPES
    )

    reason = models.CharField(
        max_length=20,
        choices=REASON_CHOICES,
        default='ADJUSTMENT'
    )

    quantity = models.PositiveIntegerField()

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='inventory_movements'
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inventory_movements'
    )

    order_item = models.ForeignKey(
        'orders.OrderItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inventory_movements'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # ==================================================
    # VALIDAR STOCK
    # ==================================================

    def clean(self):

        if self.movement_type == 'OUT':

            available_stock = self.product.stock

            if self.pk:

                old_movement = InventoryMovement.objects.get(
                    pk=self.pk
                )

                if old_movement.product_id == self.product_id:

                    if old_movement.movement_type == 'OUT':
                        available_stock += old_movement.quantity

                    else:
                        available_stock -= old_movement.quantity

            if self.quantity > available_stock:

                raise ValidationError({
                    'quantity': (
                        f'No hay suficiente stock. '
                        f'Disponible: {available_stock}'
                    )
                })

    # ==================================================
    # GUARDAR MOVIMIENTO
    # ==================================================

    @transaction.atomic
    def save(self, *args, **kwargs):

        self.full_clean()

        # ==========================================
        # SI SE ESTÁ EDITANDO UN MOVIMIENTO
        # ==========================================

        if self.pk:

            old_movement = InventoryMovement.objects.get(
                pk=self.pk
            )

            old_product = old_movement.product

            # Revertir movimiento anterior
            if old_movement.movement_type == 'IN':
                old_product.stock -= old_movement.quantity

            elif old_movement.movement_type == 'OUT':
                old_product.stock += old_movement.quantity

            old_product.save()

        # ==========================================
        # APLICAR MOVIMIENTO NUEVO
        # ==========================================

        product = Product.objects.get(
            pk=self.product_id
        )

        if self.movement_type == 'IN':
            product.stock += self.quantity

        elif self.movement_type == 'OUT':
            product.stock -= self.quantity

        product.save()

        super().save(*args, **kwargs)

    # ==================================================
    # ELIMINAR MOVIMIENTO
    # ==================================================

    @transaction.atomic
    def delete(self, *args, **kwargs):

        product = Product.objects.get(
            pk=self.product_id
        )

        # Revertir efecto del movimiento
        if self.movement_type == 'IN':
            product.stock -= self.quantity

        elif self.movement_type == 'OUT':
            product.stock += self.quantity

        product.save()

        super().delete(*args, **kwargs)

    def __str__(self):

        return (
            f'{self.product.name} - '
            f'{self.movement_type} - '
            f'{self.quantity}'
        )
