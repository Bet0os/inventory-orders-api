from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ProductViewSet,
    CategoryViewSet,
    InventoryMovementViewSet,
    SupplierViewSet,
    StockSummaryView,
    ProductStockValueView,
    LowStockView
)

router = DefaultRouter()

router.register(
    r'categories',
    CategoryViewSet,
    basename='category'
)

router.register(
    r'movements',
    InventoryMovementViewSet,
    basename='movement'
)

router.register(
    r'suppliers',
    SupplierViewSet,
    basename='supplier'
)

router.register(
    r'products',
    ProductViewSet,
    basename='product'
)

urlpatterns = [

    path(
        'reports/stock-summary/',
        StockSummaryView.as_view(),
        name='stock-summary'
    ),

    path(
        'reports/product-stock-value/',
        ProductStockValueView.as_view(),
        name='product-stock-value'
    ),

    path(
        'suppliers/low-stock/',
        LowStockView.as_view(),
        name='low-stock'
    ),

    path(
        '',
        include(router.urls)
    ),
]
