from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from .models import Order, OrderItem
from .serializers import OrderSerializer

from cart.models import Cart
from products.models import InventoryMovement


class OrderView(APIView):

    # ==========================================
    # GET - Consultar mis órdenes
    # Filtros: status y date
    # ==========================================
    def get(self, request):

        if not request.user.is_authenticated:
            return Response(
                {
                    'error': 'Debes iniciar sesión para consultar tus órdenes.'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Obtener órdenes del usuario
        orders = Order.objects.filter(
            user=request.user
        ).select_related(
            'user'
        ).prefetch_related(
            'items__product'
        )

        # ==========================================
        # FILTRO POR ESTADO
        # ==========================================
        order_status = request.query_params.get('status')

        if order_status:
            orders = orders.filter(
                status=order_status.upper()
            )

        # ==========================================
        # FILTRO POR FECHA
        # ==========================================
        date = request.query_params.get('date')

        if date:
            orders = orders.filter(
                created_at__date=date
            )

        serializer = OrderSerializer(
            orders,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    # ==========================================
    # POST - Crear una orden
    # ==========================================

    def post(self, request):

        if not request.user.is_authenticated:
            return Response(
                {
                    'error': 'Debes iniciar sesión para crear una orden.'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        # ==========================================
        # DATOS DE ENVÍO Y PAGO
        # ==========================================
        shipping_address = request.data.get('shipping_address')
        payment_method = request.data.get('payment_method')

        if not shipping_address:
            return Response(
                {
                    'error': 'Debes proporcionar una dirección de envío.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not payment_method:
            return Response(
                {
                    'error': 'Debes proporcionar un método de pago.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ==========================================
        # BUSCAR CARRITO
        # ==========================================
        try:
            cart = Cart.objects.get(
                user=request.user
            )

        except Cart.DoesNotExist:
            return Response(
                {
                    'error': 'No tienes un carrito.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # ==========================================
        # VERIFICAR CARRITO VACÍO
        # ==========================================
        if not cart.items.exists():
            return Response(
                {
                    'error': 'El carrito está vacío.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ==========================================
        # VALIDAR STOCK DISPONIBLE
        # ==========================================
        for cart_item in cart.items.select_related('product').all():

            if cart_item.quantity > cart_item.product.stock:
                return Response(
                    {
                        'error': (
                            f'No hay suficiente stock de '
                            f'{cart_item.product.name}. '
                            f'Disponible: {cart_item.product.stock}'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        # ==========================================
        # CREAR ORDEN Y DESCONTAR INVENTARIO
        # ==========================================
        with transaction.atomic():

            total = sum(
                item.subtotal
                for item in cart.items.all()
            )

            order = Order.objects.create(
                user=request.user,
                total=total,
                shipping_address=shipping_address,
                payment_method=payment_method
            )

            for cart_item in cart.items.all():

                order_item = OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price,
                    subtotal=cart_item.subtotal
                )

                # Salida de inventario por venta
                InventoryMovement.objects.create(
                    product=cart_item.product,
                    movement_type='OUT',
                    quantity=cart_item.quantity,
                    order_item=order_item
                )

            # Vaciar carrito
            cart.items.all().delete()

        serializer = OrderSerializer(order)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


# ==================================================
# ORDER DETAIL
# ==================================================

class OrderDetailView(APIView):

    # ==========================================
    # GET - Consultar una orden específica
    # ==========================================
    def get(self, request, order_id):

        if not request.user.is_authenticated:
            return Response(
                {
                    'error': 'Debes iniciar sesión para consultar la orden.'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            order = Order.objects.get(
                id=order_id,
                user=request.user
            )

        except Order.DoesNotExist:
            return Response(
                {
                    'error': 'Orden no encontrada.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrderSerializer(order)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    # ==========================================
    # PATCH - Cambiar estado de una orden
    # ==========================================

    def patch(self, request, order_id):

        if not request.user.is_authenticated:
            return Response(
                {
                    'error': 'Debes iniciar sesión para actualizar la orden.'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            order = Order.objects.get(
                id=order_id,
                user=request.user
            )

        except Order.DoesNotExist:
            return Response(
                {
                    'error': 'Orden no encontrada.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        new_status = request.data.get('status')

        if not new_status:
            return Response(
                {
                    'error': 'Debes proporcionar un status.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        new_status = new_status.upper()

        # ==========================================
        # TRANSICIONES PERMITIDAS
        # ==========================================
        allowed_transitions = {
            'PENDING': [
                'COMPLETED',
                'CANCELLED'
            ],
            'COMPLETED': [],
            'CANCELLED': [],
            'RETURNED': []
        }

        current_status = order.status

        if current_status not in allowed_transitions:
            return Response(
                {
                    'error': 'El estado actual de la orden no es válido.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if new_status not in allowed_transitions[current_status]:
            return Response(
                {
                    'error': (
                        f'No se puede cambiar una orden '
                        f'de {current_status} a {new_status}.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ==========================================
        # CAMBIAR ESTADO Y MANEJAR INVENTARIO
        # ==========================================
        with transaction.atomic():

            # Si una orden pendiente se cancela,
            # regresar productos al inventario
            if (
                current_status == 'PENDING'
                and new_status == 'CANCELLED'
            ):

                for order_item in order.items.all():

                    InventoryMovement.objects.create(
                        product=order_item.product,
                        movement_type='IN',
                        quantity=order_item.quantity,
                        order_item=order_item
                    )

            order.status = new_status
            order.save()

        serializer = OrderSerializer(order)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


# ==================================================
# ORDER RETURN
# ==================================================

class OrderReturnView(APIView):

    # ==========================================
    # POST - Devolver una orden
    # ==========================================
    def post(self, request, order_id):

        if not request.user.is_authenticated:
            return Response(
                {
                    'error': 'Debes iniciar sesión para devolver una orden.'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            order = Order.objects.get(
                id=order_id,
                user=request.user
            )

        except Order.DoesNotExist:
            return Response(
                {
                    'error': 'Orden no encontrada.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # ==========================================
        # VERIFICAR ESTADO
        # ==========================================
        if order.status == 'RETURNED':
            return Response(
                {
                    'error': 'La orden ya fue devuelta.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if order.status != 'COMPLETED':
            return Response(
                {
                    'error': 'Solo se pueden devolver órdenes completadas.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ==========================================
        # DEVOLVER PRODUCTOS AL INVENTARIO
        # ==========================================
        with transaction.atomic():

            for order_item in order.items.all():

                InventoryMovement.objects.create(
                    product=order_item.product,
                    movement_type='IN',
                    quantity=order_item.quantity,
                    order_item=order_item
                )

            order.status = 'RETURNED'
            order.save()

        serializer = OrderSerializer(order)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
