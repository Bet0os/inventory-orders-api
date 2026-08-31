from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):

    def has_permission(self, request, view):

        # Consultar productos sí está permitido
        if request.method in SAFE_METHODS:
            return True

        # Crear, editar o eliminar:
        # solamente administradores
        return (
            request.user.is_authenticated
            and request.user.is_staff
        )
