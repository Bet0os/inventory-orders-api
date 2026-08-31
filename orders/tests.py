from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from cart.models import Cart, CartItem
from products.models import Category, Supplier, Product
from .models import Order


User = get_user_model()


class OrderAPITests(APITestCase):

    def setUp(self):

        # ==========================================
        # USUARIOS
        # ==========================================

        self.user = User.objects.create_user(
            username='cliente_test',
            password='Cliente12345'
        )

        self.other_user = User.objects.create_user(
            username='otro_cliente',
            password='Otro12345'
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

        # ==========================================
        # AUTENTICAR USUARIO
        # ==========================================

        self.client.force_authenticate(
            user=self.user
        )

    # ==================================================
    # CREAR ORDEN DESDE CARRITO
    # ==================================================

    def test_create_order_from_cart(self):

        cart = Cart.objects.create(
            user=self.user
        )

        CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=2
        )

        data = {
            'shipping_address': '123 Main St',
            'payment_method': 'CARD'
        }

        response = self.client.post(
            '/api/orders/',
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            response.data['shipping_address'],
            '123 Main St'
        )

        self.assertEqual(
            response.data['payment_method'],
            'CARD'
        )

        self.assertEqual(
            float(response.data['total']),
            30000.0
        )

    # ==================================================
    # CARRITO SE VACÍA AL CREAR ORDEN
    # ==================================================

    def test_cart_is_empty_after_order(self):

        cart = Cart.objects.create(
            user=self.user
        )

        CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=1
        )

        response = self.client.post(
            '/api/orders/',
            {
                'shipping_address': '123 Main St',
                'payment_method': 'CARD'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            cart.items.count(),
            0
        )

    # ==================================================
    # STOCK SE ACTUALIZA AL CREAR ORDEN
    # ==================================================

    def test_stock_decreases_after_order(self):

        cart = Cart.objects.create(
            user=self.user
        )

        CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=2
        )

        self.client.post(
            '/api/orders/',
            {
                'shipping_address': '123 Main St',
                'payment_method': 'CARD'
            },
            format='json'
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            8
        )

    # ==================================================
    # NO PERMITIR ORDEN CON STOCK INSUFICIENTE
    # ==================================================

    def test_cannot_create_order_with_insufficient_stock(self):

        cart = Cart.objects.create(
            user=self.user
        )

        CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=20
        )

        response = self.client.post(
            '/api/orders/',
            {
                'shipping_address': '123 Main St',
                'payment_method': 'CARD'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            Order.objects.count(),
            0
        )

    # ==================================================
    # DIRECCIÓN DE ENVÍO OBLIGATORIA
    # ==================================================

    def test_shipping_address_is_required(self):

        cart = Cart.objects.create(
            user=self.user
        )

        CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=1
        )

        response = self.client.post(
            '/api/orders/',
            {
                'payment_method': 'CARD'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    # ==================================================
    # MÉTODO DE PAGO OBLIGATORIO
    # ==================================================

    def test_payment_method_is_required(self):

        cart = Cart.objects.create(
            user=self.user
        )

        CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=1
        )

        response = self.client.post(
            '/api/orders/',
            {
                'shipping_address': '123 Main St'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    # ==================================================
    # LISTAR SOLO ÓRDENES DEL USUARIO
    # ==================================================

    def test_user_only_sees_own_orders(self):

        Order.objects.create(
            user=self.user,
            total=15000,
            status='PENDING',
            shipping_address='Dirección 1',
            payment_method='CARD'
        )

        Order.objects.create(
            user=self.other_user,
            total=5000,
            status='PENDING',
            shipping_address='Dirección 2',
            payment_method='CASH'
        )

        response = self.client.get(
            '/api/orders/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            1
        )

        self.assertEqual(
            response.data[0]['user'],
            self.user.id
        )

    # ==================================================
    # FILTRO POR STATUS
    # ==================================================

    def test_filter_orders_by_status(self):

        Order.objects.create(
            user=self.user,
            total=15000,
            status='PENDING',
            shipping_address='Dirección 1',
            payment_method='CARD'
        )

        Order.objects.create(
            user=self.user,
            total=5000,
            status='COMPLETED',
            shipping_address='Dirección 2',
            payment_method='CASH'
        )

        response = self.client.get(
            '/api/orders/?status=PENDING'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            1
        )

        self.assertEqual(
            response.data[0]['status'],
            'PENDING'
        )

    # ==================================================
    # VER ORDEN ESPECÍFICA PROPIA
    # ==================================================

    def test_get_own_order_detail(self):

        order = Order.objects.create(
            user=self.user,
            total=15000,
            status='PENDING',
            shipping_address='Dirección 1',
            payment_method='CARD'
        )

        response = self.client.get(
            f'/api/orders/{order.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['id'],
            order.id
        )

    # ==================================================
    # NO VER ORDEN DE OTRO USUARIO
    # ==================================================

    def test_cannot_view_another_users_order(self):

        order = Order.objects.create(
            user=self.other_user,
            total=15000,
            status='PENDING',
            shipping_address='Dirección 2',
            payment_method='CARD'
        )

        response = self.client.get(
            f'/api/orders/{order.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    # ==================================================
    # CANCELAR ORDEN RESTAURA STOCK
    # ==================================================

    def test_cancel_order_restores_stock(self):

        cart = Cart.objects.create(
            user=self.user
        )

        CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=2
        )

        create_response = self.client.post(
            '/api/orders/',
            {
                'shipping_address': '123 Main St',
                'payment_method': 'CARD'
            },
            format='json'
        )

        order_id = create_response.data['id']

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            8
        )

        response = self.client.patch(
            f'/api/orders/{order_id}/',
            {
                'status': 'CANCELLED'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            10
        )
