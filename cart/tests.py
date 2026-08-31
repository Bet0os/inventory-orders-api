from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from products.models import Category, Supplier, Product
from .models import Cart, CartItem


User = get_user_model()


class CartAPITests(APITestCase):

    def setUp(self):

        # ==========================================
        # USUARIO
        # ==========================================

        self.user = User.objects.create_user(
            username='cliente_test',
            password='Cliente12345'
        )

        # ==========================================
        # CATEGORÍA
        # ==========================================

        self.category = Category.objects.create(
            name='Electrónica',
            description='Productos electrónicos'
        )

        # ==========================================
        # PROVEEDOR
        # ==========================================

        self.supplier = Supplier.objects.create(
            name='Tech Supplier',
            contact_email='ventas@techsupplier.com',
            phone='5551234567'
        )

        # ==========================================
        # PRODUCTO
        # ==========================================

        self.product = Product.objects.create(
            name='Laptop',
            sku='LAP-001',
            price=15000,
            stock=10,
            category=self.category,
            supplier=self.supplier
        )

        self.client.force_authenticate(
            user=self.user
        )

    # ==================================================
    # VER CARRITO
    # ==================================================

    def test_get_cart(self):

        response = self.client.get(
            '/api/cart/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['user'],
            self.user.id
        )

        self.assertIn(
            'items',
            response.data
        )

        self.assertIn(
            'total',
            response.data
        )

    # ==================================================
    # AGREGAR PRODUCTO AL CARRITO
    # ==================================================

    def test_add_product_to_cart(self):

        data = {
            'product': self.product.id,
            'quantity': 2
        }

        response = self.client.post(
            '/api/cart/',
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        cart = Cart.objects.get(
            user=self.user
        )

        cart_item = CartItem.objects.get(
            cart=cart,
            product=self.product
        )

        self.assertEqual(
            cart_item.quantity,
            2
        )

    # ==================================================
    # SUBTOTAL Y TOTAL
    # ==================================================

    def test_cart_total(self):

        self.client.post(
            '/api/cart/',
            {
                'product': self.product.id,
                'quantity': 2
            },
            format='json'
        )

        response = self.client.get(
            '/api/cart/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            float(response.data['total']),
            30000.0
        )

    # ==================================================
    # NO PERMITIR STOCK INSUFICIENTE
    # ==================================================

    def test_cannot_add_more_than_available_stock(self):

        data = {
            'product': self.product.id,
            'quantity': 20
        }

        response = self.client.post(
            '/api/cart/',
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            response.data['stock_disponible'],
            10
        )

    # ==================================================
    # MODIFICAR CANTIDAD
    # ==================================================

    def test_update_cart_item_quantity(self):

        cart = Cart.objects.create(
            user=self.user
        )

        cart_item = CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=1
        )

        response = self.client.patch(
            f'/api/cart/items/{cart_item.id}/',
            {
                'quantity': 3
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        cart_item.refresh_from_db()

        self.assertEqual(
            cart_item.quantity,
            3
        )

    # ==================================================
    # NO PERMITIR MODIFICAR A STOCK INSUFICIENTE
    # ==================================================

    def test_cannot_update_cart_above_stock(self):

        cart = Cart.objects.create(
            user=self.user
        )

        cart_item = CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=1
        )

        response = self.client.patch(
            f'/api/cart/items/{cart_item.id}/',
            {
                'quantity': 50
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    # ==================================================
    # ELIMINAR PRODUCTO DEL CARRITO
    # ==================================================

    def test_delete_cart_item(self):

        cart = Cart.objects.create(
            user=self.user
        )

        cart_item = CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=1
        )

        response = self.client.delete(
            f'/api/cart/items/{cart_item.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertFalse(
            CartItem.objects.filter(
                id=cart_item.id
            ).exists()
        )

    # ==================================================
    # UN USUARIO NO PUEDE EDITAR ITEM DE OTRO CARRITO
    # ==================================================

    def test_user_cannot_edit_another_users_cart_item(self):

        other_user = User.objects.create_user(
            username='otro_usuario',
            password='Otro12345'
        )

        other_cart = Cart.objects.create(
            user=other_user
        )

        other_item = CartItem.objects.create(
            cart=other_cart,
            product=self.product,
            quantity=1
        )

        response = self.client.patch(
            f'/api/cart/items/{other_item.id}/',
            {
                'quantity': 2
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )
