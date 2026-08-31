from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from django.db import transaction

from .models import Order, OrderItem
from .serializers import OrderSerializer

from cart.models import Cart
from products.models import InventoryMovement


# ==================================================
# ORDERS
# ==================================================

class OrderView(APIView):

    permission_classes = [IsAuthenticated]

    # ==========================================
    # GET - CONSULTAR ÓRDENES
    # Cliente: solamente sus órdenes
    # Staff: todas las órdenes
    #
    # Filtros:
    # ?status=PENDING
    # ?date=2026-08-31
    # ==========================================

    def get(self, request):

        # ==========================================
        # STAFF PUEDE VER TODAS LAS ÓRDENES
        # ==========================================

        if request.user.is_staff:

            orders = Order.objects.all()

        # ==========================================
        # CLIENTE SOLO PUEDE VER SUS ÓRDENES
        # ==========================================

        else:

            orders = Order.objects.filter(
                user=request.user
            )

        # ==========================================
        # OPTIMIZACIÓN DE CONSULTAS
        # ==========================================

        orders = orders.select_related(
            'user'
        ).prefetch_related(
            'items__product'
        )

        # ==========================================
        # FILTRO POR ESTADO
        # ==========================================

        order_status = request.query_params.get(
            'status'
        )

        if order_status:

            orders = orders.filter(
                status=order_status.upper()
            )

        # ==========================================
        # FILTRO POR FECHA
        # ==========================================

        date = request.query_params.get(
            'date'
        )

        if date:

            orders = orders.filter(
                created_at__date=date
            )

        # ==========================================
        # ORDENAR
        # ==========================================

        orders = orders.order_by(
            '-created_at'
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
    # POST - CREAR UNA ORDEN DESDE EL CARRITO
    # ==========================================

    def post(self, request):

        # ==========================================
        # DATOS DE ENVÍO Y PAGO
        # ==========================================

        shipping_address = request.data.get(
            'shipping_address'
        )

        payment_method = request.data.get(
            'payment_method'
        )

        # ==========================================
        # VALIDAR DIRECCIÓN
        # ==========================================

        if not shipping_address:

            return Response(
                {
                    'error': (
                        'Debes proporcionar '
                        'una dirección de envío.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ==========================================
        # VALIDAR MÉTODO DE PAGO
        # ==========================================

        if not payment_method:

            return Response(
                {
                    'error': (
                        'Debes proporcionar '
                        'un método de pago.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ==========================================
        # BUSCAR CARRITO DEL USUARIO
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
        # OBTENER ITEMS
        # ==========================================

        cart_items = cart.items.select_related(
            'product'
        ).all()

        # ==========================================
        # VALIDAR STOCK
        # ==========================================

        for cart_item in cart_items:

            if cart_item.quantity > cart_item.product.stock:

                return Response(
                    {
                        'error': (
                            f'No hay suficiente stock de '
                            f'{cart_item.product.name}. '
                            f'Disponible: '
                            f'{cart_item.product.stock}'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        # ==========================================
        # CREAR ORDEN
        # ==========================================

        with transaction.atomic():

            total = sum(
                item.subtotal
                for item in cart_items
            )

            order = Order.objects.create(
                user=request.user,
                total=total,
                shipping_address=shipping_address,
                payment_method=payment_method
            )

            # ======================================
            # CREAR ORDER ITEMS
            # ======================================

            for cart_item in cart_items:

                order_item = OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price,
                    subtotal=cart_item.subtotal
                )

                # ==================================
                # SALIDA DE INVENTARIO POR VENTA
                # ==================================

                InventoryMovement.objects.create(
                    product=cart_item.product,
                    movement_type='OUT',
                    reason='SALE',
                    quantity=cart_item.quantity,
                    order_item=order_item
                )

            # ======================================
            # VACIAR CARRITO
            # ======================================

            cart.items.all().delete()

        serializer = OrderSerializer(
            order
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


# ==================================================
# ORDER DETAIL
# ==================================================

class OrderDetailView(APIView):

    permission_classes = [IsAuthenticated]

    # ==========================================
    # OBTENER ORDEN SEGÚN PERMISOS
    #
    # Staff:
    # puede acceder a cualquier orden
    #
    # Cliente:
    # solamente puede acceder a sus órdenes
    # ==========================================

    def get_order(self, request, order_id):

        try:

            if request.user.is_staff:

                return Order.objects.get(
                    id=order_id
                )

            return Order.objects.get(
                id=order_id,
                user=request.user
            )

        except Order.DoesNotExist:

            return None

    # ==========================================
    # GET - CONSULTAR ORDEN ESPECÍFICA
    # ==========================================

    def get(self, request, order_id):

        order = self.get_order(
            request,
            order_id
        )

        if not order:

            return Response(
                {
                    'error': 'Orden no encontrada.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrderSerializer(
            order
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    # ==========================================
    # PATCH - CAMBIAR ESTADO
    #
    # Cliente:
    # PENDING -> CANCELLED
    #
    # Staff:
    # PENDING -> COMPLETED
    # PENDING -> CANCELLED
    # ==========================================

    def patch(self, request, order_id):

        order = self.get_order(
            request,
            order_id
        )

        if not order:

            return Response(
                {
                    'error': 'Orden no encontrada.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # ==========================================
        # OBTENER NUEVO ESTADO
        # ==========================================

        new_status = request.data.get(
            'status'
        )

        if not new_status:

            return Response(
                {
                    'error': (
                        'Debes proporcionar un status.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        new_status = new_status.upper()

        current_status = order.status

        # ==========================================
        # VALIDAR STATUS EXISTENTE
        # ==========================================

        valid_statuses = [
            'PENDING',
            'COMPLETED',
            'CANCELLED',
            'RETURNED'
        ]

        if new_status not in valid_statuses:

            return Response(
                {
                    'error': 'El status proporcionado no es válido.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ==========================================
        # NO MODIFICAR ÓRDENES FINALIZADAS
        # ==========================================

        if current_status in [
            'COMPLETED',
            'CANCELLED',
            'RETURNED'
        ]:

            return Response(
                {
                    'error': (
                        f'No se puede cambiar una orden '
                        f'que está en estado '
                        f'{current_status}.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ==========================================
        # CLIENTE
        # SOLO PUEDE CANCELAR UNA ORDEN PENDING
        # ==========================================

        if not request.user.is_staff:

            if new_status != 'CANCELLED':

                return Response(
                    {
                        'error': (
                            'Los clientes solamente '
                            'pueden cancelar órdenes '
                            'pendientes.'
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

        # ==========================================
        # STAFF
        # PUEDE COMPLETAR O CANCELAR
        # ==========================================

        else:

            allowed_staff_statuses = [
                'COMPLETED',
                'CANCELLED'
            ]

            if new_status not in allowed_staff_statuses:

                return Response(
                    {
                        'error': (
                            'El administrador solamente '
                            'puede marcar la orden como '
                            'COMPLETED o CANCELLED.'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        # ==========================================
        # ACTUALIZAR ESTADO
        # ==========================================

        with transaction.atomic():

            # ======================================
            # SI SE CANCELA, RESTAURAR STOCK
            # ======================================

            if (
                current_status == 'PENDING'
                and new_status == 'CANCELLED'
            ):

                for order_item in order.items.all():

                    InventoryMovement.objects.create(
                        product=order_item.product,
                        movement_type='IN',
                        reason='ADJUSTMENT',
                        quantity=order_item.quantity,
                        order_item=order_item
                    )

            order.status = new_status
            order.save()

        serializer = OrderSerializer(
            order
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


# ==================================================
# ORDER RETURN
# ==================================================

class OrderReturnView(APIView):

    permission_classes = [IsAuthenticated]

    # ==========================================
    # OBTENER ORDEN SEGÚN PERMISOS
    # ==========================================

    def get_order(self, request, order_id):

        try:

            if request.user.is_staff:

                return Order.objects.get(
                    id=order_id
                )

            return Order.objects.get(
                id=order_id,
                user=request.user
            )

        except Order.DoesNotExist:

            return None

    # ==========================================
    # POST - DEVOLVER UNA ORDEN
    # ==========================================

    def post(self, request, order_id):

        order = self.get_order(
            request,
            order_id
        )

        if not order:

            return Response(
                {
                    'error': 'Orden no encontrada.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # ==========================================
        # YA FUE DEVUELTA
        # ==========================================

        if order.status == 'RETURNED':

            return Response(
                {
                    'error': (
                        'La orden ya fue devuelta.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ==========================================
        # SOLO COMPLETED PUEDE DEVOLVERSE
        # ==========================================

        if order.status != 'COMPLETED':

            return Response(
                {
                    'error': (
                        'Solo se pueden devolver '
                        'órdenes completadas.'
                    )
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
                    reason='ADJUSTMENT',
                    quantity=order_item.quantity,
                    order_item=order_item
                )

            order.status = 'RETURNED'
            order.save()

        serializer = OrderSerializer(
            order
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
