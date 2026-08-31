from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Cart, CartItem
from .serializers import CartSerializer
from products.models import Product


# ==================================================
# CART
# ==================================================

class CartView(APIView):

    permission_classes = [IsAuthenticated]

    def get_cart(self, request):

        cart, created = Cart.objects.get_or_create(
            user=request.user
        )

        return cart

    # =========================
    # GET /api/cart/
    # =========================

    def get(self, request):

        cart = self.get_cart(request)

        serializer = CartSerializer(cart)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    # =========================
    # POST /api/cart/
    # =========================

    def post(self, request):

        cart = self.get_cart(request)

        product_id = request.data.get('product')
        quantity = request.data.get('quantity', 1)

        # ==========================================
        # VALIDAR PRODUCTO
        # ==========================================

        if not product_id:

            return Response(
                {
                    'error': 'Debes proporcionar el producto.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ==========================================
        # BUSCAR PRODUCTO
        # ==========================================

        try:

            product = Product.objects.get(
                id=product_id
            )

        except Product.DoesNotExist:

            return Response(
                {
                    'error': 'El producto no existe.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # ==========================================
        # VALIDAR CANTIDAD
        # ==========================================

        try:

            quantity = int(quantity)

        except (TypeError, ValueError):

            return Response(
                {
                    'error': (
                        'La cantidad debe ser '
                        'un número entero.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantity <= 0:

            return Response(
                {
                    'error': (
                        'La cantidad debe ser '
                        'mayor que 0.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ==========================================
        # VALIDAR STOCK
        # ==========================================

        if quantity > product.stock:

            return Response(
                {
                    'error': 'No hay suficiente stock.',
                    'stock_disponible': product.stock
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ==========================================
        # AGREGAR PRODUCTO AL CARRITO
        # ==========================================

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={
                'quantity': quantity
            }
        )

        # ==========================================
        # SI YA EXISTÍA, AUMENTAR CANTIDAD
        # ==========================================

        if not created:

            nueva_cantidad = (
                cart_item.quantity + quantity
            )

            if nueva_cantidad > product.stock:

                return Response(
                    {
                        'error': (
                            'No hay suficiente stock '
                            'para agregar esa cantidad.'
                        ),
                        'stock_disponible': product.stock,
                        'cantidad_en_carrito': (
                            cart_item.quantity
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            cart_item.quantity = nueva_cantidad
            cart_item.save()

        serializer = CartSerializer(cart)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


# ==================================================
# CART ITEM
# ==================================================

class CartItemView(APIView):

    permission_classes = [IsAuthenticated]

    def get_cart(self, request):

        cart, created = Cart.objects.get_or_create(
            user=request.user
        )

        return cart

    # =========================
    # PATCH /api/cart/items/<id>/
    # =========================

    def patch(self, request, item_id):

        cart = self.get_cart(request)

        # ==========================================
        # BUSCAR ITEM DEL CARRITO ACTUAL
        # ==========================================

        try:

            cart_item = CartItem.objects.get(
                id=item_id,
                cart=cart
            )

        except CartItem.DoesNotExist:

            return Response(
                {
                    'error': (
                        'El producto no está '
                        'en tu carrito.'
                    )
                },
                status=status.HTTP_404_NOT_FOUND
            )

        quantity = request.data.get('quantity')

        # ==========================================
        # VALIDAR CANTIDAD
        # ==========================================

        if quantity is None:

            return Response(
                {
                    'error': (
                        'Debes proporcionar '
                        'la cantidad.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            quantity = int(quantity)

        except (TypeError, ValueError):

            return Response(
                {
                    'error': (
                        'La cantidad debe ser '
                        'un número entero.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantity <= 0:

            return Response(
                {
                    'error': (
                        'La cantidad debe ser '
                        'mayor que 0.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ==========================================
        # VALIDAR STOCK
        # ==========================================

        if quantity > cart_item.product.stock:

            return Response(
                {
                    'error': 'No hay suficiente stock.',
                    'stock_disponible': (
                        cart_item.product.stock
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ==========================================
        # ACTUALIZAR CANTIDAD
        # ==========================================

        cart_item.quantity = quantity
        cart_item.save()

        serializer = CartSerializer(cart)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    # =========================
    # DELETE /api/cart/items/<id>/
    # =========================

    def delete(self, request, item_id):

        cart = self.get_cart(request)

        # ==========================================
        # BUSCAR ITEM DEL CARRITO ACTUAL
        # ==========================================

        try:

            cart_item = CartItem.objects.get(
                id=item_id,
                cart=cart
            )

        except CartItem.DoesNotExist:

            return Response(
                {
                    'error': (
                        'El producto no está '
                        'en tu carrito.'
                    )
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # ==========================================
        # ELIMINAR ITEM
        # ==========================================

        cart_item.delete()

        serializer = CartSerializer(cart)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
