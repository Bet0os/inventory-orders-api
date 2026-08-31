from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from django.db.models import (
    Q,
    Sum,
    F,
    DecimalField,
    ExpressionWrapper
)

from .permissions import IsAdminOrReadOnly

from .models import (
    Product,
    Category,
    Supplier,
    InventoryMovement
)

from .serializers import (
    ProductSerializer,
    CategorySerializer,
    SupplierSerializer,
    InventoryHistorySerializer,
    InventoryMovementSerializer
)


# ==================================================
# PRODUCTS
# ==================================================

class ProductViewSet(viewsets.ModelViewSet):

    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):

        queryset = Product.objects.all()

        category = self.request.query_params.get('category')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        stock = self.request.query_params.get('stock')
        search = self.request.query_params.get('search')

        # ==========================================
        # FILTRO POR CATEGORÍA
        # ==========================================

        if category:
            queryset = queryset.filter(
                category_id=category
            )

        # ==========================================
        # FILTRO POR PRECIO MÍNIMO
        # ==========================================

        if min_price:
            queryset = queryset.filter(
                price__gte=min_price
            )

        # ==========================================
        # FILTRO POR PRECIO MÁXIMO
        # ==========================================

        if max_price:
            queryset = queryset.filter(
                price__lte=max_price
            )

        # ==========================================
        # FILTRO POR STOCK
        # ==========================================

        if stock:
            queryset = queryset.filter(
                stock=stock
            )

        # ==========================================
        # BÚSQUEDA CON Q OBJECTS
        # ==========================================

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(sku__icontains=search)
            )

        return queryset

    # ==========================================
    # HISTORIAL DE INVENTARIO POR PRODUCTO
    # GET /api/products/<id>/inventory/
    # ==========================================

    @action(
        detail=True,
        methods=['get'],
        url_path='inventory'
    )
    def inventory(self, request, pk=None):

        product = self.get_object()

        movements = InventoryMovement.objects.filter(
            product=product
        ).order_by(
            '-created_at'
        )

        movement_serializer = InventoryHistorySerializer(
            movements,
            many=True
        )

        product_serializer = ProductSerializer(
            product
        )

        return Response(
            {
                'product': product_serializer.data,
                'inventory_history': movement_serializer.data
            }
        )


# ==================================================
# CATEGORY PAGINATION
# ==================================================

class CategoryPagination(PageNumberPagination):

    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50


# ==================================================
# CATEGORIES
# ==================================================

class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer
    pagination_class = CategoryPagination
    permission_classes = [IsAdminOrReadOnly]


# ==================================================
# SUPPLIERS
# ==================================================

class SupplierViewSet(viewsets.ModelViewSet):

    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAdminOrReadOnly]


# ==================================================
# INVENTORY MOVEMENTS
# ==================================================

class InventoryMovementViewSet(viewsets.ModelViewSet):

    queryset = InventoryMovement.objects.all()
    serializer_class = InventoryMovementSerializer
    permission_classes = [IsAdminOrReadOnly]


# ==================================================
# STOCK SUMMARY REPORT
# ==================================================

class StockSummaryView(APIView):

    def get(self, request):

        products = Product.objects.all()

        # ==========================================
        # TOTAL DE PRODUCTOS
        # ==========================================

        total_products = products.count()

        # ==========================================
        # TOTAL DE STOCK
        # ==========================================

        total_stock = products.aggregate(
            total_stock=Sum('stock')
        )['total_stock'] or 0

        # ==========================================
        # VALOR TOTAL DEL INVENTARIO
        # ==========================================

        inventory_value = products.aggregate(
            inventory_value=Sum(
                ExpressionWrapper(
                    F('price') * F('stock'),
                    output_field=DecimalField(
                        max_digits=15,
                        decimal_places=2
                    )
                )
            )
        )['inventory_value'] or 0

        return Response(
            {
                'total_products': total_products,
                'total_stock': total_stock,
                'inventory_value': inventory_value
            }
        )


# ==================================================
# PRODUCT STOCK VALUE
# ==================================================

class ProductStockValueView(APIView):

    def get(self, request):

        products = Product.objects.annotate(
            stock_value=ExpressionWrapper(
                F('price') * F('stock'),
                output_field=DecimalField(
                    max_digits=15,
                    decimal_places=2
                )
            )
        ).values(
            'id',
            'name',
            'price',
            'stock',
            'stock_value'
        )

        return Response(
            products
        )


# ==================================================
# SUPPLIERS WITH LOW STOCK
# GET /api/suppliers/low-stock/
# ==================================================

class LowStockView(APIView):

    def get(self, request):

        suppliers = Supplier.objects.filter(
            products__stock__lt=10
        ).distinct()

        serializer = SupplierSerializer(
            suppliers,
            many=True
        )

        return Response(
            serializer.data
        )
