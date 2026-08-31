from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import (
    Category,
    Supplier,
    Product,
    InventoryMovement
)


User = get_user_model()


class ProductAPITests(APITestCase):

    def setUp(self):

        # ==========================================
        # USUARIOS
        # ==========================================

        self.admin = User.objects.create_user(
            username='admin_test',
            password='Admin12345',
            is_staff=True
        )

        self.client_user = User.objects.create_user(
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
        # PRODUCTOS
        # ==========================================

        self.product = Product.objects.create(
            name='Laptop',
            sku='LAP-001',
            price=15000,
            stock=20,
            category=self.category,
            supplier=self.supplier
        )

        self.low_stock_product = Product.objects.create(
            name='Mouse',
            sku='MOU-001',
            price=500,
            stock=5,
            category=self.category,
            supplier=self.supplier
        )

    # ==================================================
    # LISTAR PRODUCTOS
    # ==================================================

    def test_list_products(self):

        response = self.client.get(
            '/api/products/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    # ==================================================
    # VER PRODUCTO ESPECÍFICO
    # ==================================================

    def test_product_detail(self):

        response = self.client.get(
            f'/api/products/{self.product.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['name'],
            'Laptop'
        )

    # ==================================================
    # CLIENTE NO PUEDE CREAR PRODUCTO
    # ==================================================

    def test_normal_user_cannot_create_product(self):

        self.client.force_authenticate(
            user=self.client_user
        )

        data = {
            'name': 'Teclado',
            'sku': 'TEC-001',
            'price': '800.00',
            'stock': 10,
            'category': self.category.id,
            'supplier': self.supplier.id
        }

        response = self.client.post(
            '/api/products/',
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    # ==================================================
    # ADMIN SÍ PUEDE CREAR PRODUCTO
    # ==================================================

    def test_admin_can_create_product(self):

        self.client.force_authenticate(
            user=self.admin
        )

        data = {
            'name': 'Teclado',
            'sku': 'TEC-001',
            'price': '800.00',
            'stock': 10,
            'category': self.category.id,
            'supplier': self.supplier.id
        }

        response = self.client.post(
            '/api/products/',
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    # ==================================================
    # SKU DEBE SER ÚNICO
    # ==================================================

    def test_sku_must_be_unique(self):

        self.client.force_authenticate(
            user=self.admin
        )

        data = {
            'name': 'Laptop duplicada',
            'sku': 'LAP-001',
            'price': '10000.00',
            'stock': 5,
            'category': self.category.id,
            'supplier': self.supplier.id
        }

        response = self.client.post(
            '/api/products/',
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    # ==================================================
    # FILTRO POR CATEGORÍA
    # ==================================================

    def test_filter_products_by_category(self):

        response = self.client.get(
            f'/api/products/?category={self.category.id}'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            2
        )

    # ==================================================
    # FILTRO POR PRECIO
    # ==================================================

    def test_filter_products_by_min_price(self):

        response = self.client.get(
            '/api/products/?min_price=10000'
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
            response.data[0]['name'],
            'Laptop'
        )

    # ==================================================
    # FILTRO POR STOCK
    # ==================================================

    def test_filter_products_by_stock(self):

        response = self.client.get(
            '/api/products/?stock=5'
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
            response.data[0]['name'],
            'Mouse'
        )

    # ==================================================
    # BÚSQUEDA CON Q OBJECTS
    # ==================================================

    def test_search_product_by_name(self):

        response = self.client.get(
            '/api/products/?search=Laptop'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            1
        )

    # ==================================================
    # HISTORIAL DE INVENTARIO POR PRODUCTO
    # ==================================================

    def test_product_inventory_history(self):

        InventoryMovement.objects.create(
            product=self.product,
            movement_type='IN',
            quantity=3,
            reason='ADJUSTMENT'
        )

        response = self.client.get(
            f'/api/products/{self.product.id}/inventory/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertIn(
            'product',
            response.data
        )

        self.assertIn(
            'inventory_history',
            response.data
        )

        self.assertEqual(
            response.data['product']['id'],
            self.product.id
        )

        self.assertEqual(
            len(response.data['inventory_history']),
            1
        )

    # ==================================================
    # PROVEEDORES CON STOCK BAJO
    # ==================================================

    def test_low_stock_suppliers(self):

        response = self.client.get(
            '/api/suppliers/low-stock/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        supplier_ids = [
            supplier['id']
            for supplier in response.data
        ]

        self.assertIn(
            self.supplier.id,
            supplier_ids
        )

    # ==================================================
    # STOCK SUMMARY
    # ==================================================

    def test_stock_summary(self):

        response = self.client.get(
            '/api/reports/stock-summary/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertIn(
            'total_products',
            response.data
        )

        self.assertIn(
            'total_stock',
            response.data
        )

        self.assertIn(
            'inventory_value',
            response.data
        )


class CategoryAPITests(APITestCase):

    def setUp(self):

        for number in range(6):

            Category.objects.create(
                name=f'Categoría {number}',
                description='Categoría de prueba'
            )

    # ==================================================
    # PAGINACIÓN DE CATEGORÍAS
    # ==================================================

    def test_categories_are_paginated(self):

        response = self.client.get(
            '/api/categories/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertIn(
            'count',
            response.data
        )

        self.assertIn(
            'results',
            response.data
        )

        # Configuramos page_size = 5
        self.assertEqual(
            len(response.data['results']),
            5
        )

        self.assertEqual(
            response.data['count'],
            6
        )
