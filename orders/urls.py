from django.urls import path

from .views import OrderView, OrderDetailView, OrderReturnView


urlpatterns = [
    path('', OrderView.as_view(), name='order-list'),
    path('<int:order_id>/', OrderDetailView.as_view(), name='order-detail'),
    path('<int:order_id>/return/', OrderReturnView.as_view(), name='order-return'),
]
