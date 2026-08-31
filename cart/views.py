from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Cart, CartItem
from .serializers import CartSerializer
from products.models import Product


class CartView(APIView):

    def get_cart(self, request):

        # Usuario autenticado
        if request.user.is_authenticated:

            cart, created = Cart.objects.get_or_create(
                user=request.user
            )

        # Usuario invitado
        else:

            if not request.session.session_key:
                request.session.create()

            session_key = request.session.session_key

            cart, created = Cart.objects.get_or_create(
                session_key=session_key
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

        # Verificar que se haya enviado el producto
        if not product_id:
            return Response(
                {'error': 'Debes proporcionar el producto.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Buscar producto
        try:
            product = Product.objects.get(id=product_id)

        except Product.DoesNotExist:
            return Response(
                {'error': 'El producto no existe.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Convertir cantidad a entero
        try:
            quantity = int(quantity)

        except (TypeError, ValueError):
            return Response(
                {'error': 'La cantidad debe ser un número entero.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar cantidad
        if quantity <= 0:
            return Response(
                {'error': 'La cantidad debe ser mayor que 0.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar stock
        if quantity > product.stock:
            return Response(
                {
                    'error': 'No hay suficiente stock.',
                    'stock_disponible': product.stock
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Buscar si ya existe el producto en el carrito
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        # Si ya existe, aumentar cantidad
        if not created:

            nueva_cantidad = cart_item.quantity + quantity

            # Verificar stock considerando lo que ya había
            if nueva_cantidad > product.stock:
                return Response(
                    {
                        'error': 'No hay suficiente stock para agregar esa cantidad.',
                        'stock_disponible': product.stock,
                        'cantidad_en_carrito': cart_item.quantity
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


# ==========================================
# CART ITEM
# ==========================================

class CartItemView(APIView):

    def get_cart(self, request):

        # Usuario autenticado
        if request.user.is_authenticated:

            cart, created = Cart.objects.get_or_create(
                user=request.user
            )

        # Usuario invitado
        else:

            if not request.session.session_key:
                request.session.create()

            session_key = request.session.session_key

            cart, created = Cart.objects.get_or_create(
                session_key=session_key
            )

        return cart

    # =========================
    # PATCH /api/cart/items/<id>/
    # =========================

    def patch(self, request, item_id):

        cart = self.get_cart(request)

        # Buscar el item SOLO dentro del carrito actual
        try:
            cart_item = CartItem.objects.get(
                id=item_id,
                cart=cart
            )

        except CartItem.DoesNotExist:
            return Response(
                {'error': 'El producto no está en tu carrito.'},
                status=status.HTTP_404_NOT_FOUND
            )

        quantity = request.data.get('quantity')

        # Verificar que se haya enviado quantity
        if quantity is None:
            return Response(
                {'error': 'Debes proporcionar la cantidad.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Convertir a entero
        try:
            quantity = int(quantity)

        except (TypeError, ValueError):
            return Response(
                {'error': 'La cantidad debe ser un número entero.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar cantidad
        if quantity <= 0:
            return Response(
                {'error': 'La cantidad debe ser mayor que 0.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar stock
        if quantity > cart_item.product.stock:
            return Response(
                {
                    'error': 'No hay suficiente stock.',
                    'stock_disponible': cart_item.product.stock
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Actualizar cantidad
        cart_item.quantity = quantity
        cart_item.save()

        # Devolver carrito actualizado
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

        # Buscar el item SOLO dentro del carrito actual
        try:
            cart_item = CartItem.objects.get(
                id=item_id,
                cart=cart
            )

        except CartItem.DoesNotExist:
            return Response(
                {'error': 'El producto no está en tu carrito.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Eliminar producto
        cart_item.delete()

        # Devolver carrito actualizado
        serializer = CartSerializer(cart)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
