"""
=====================================================================
 PERMISOS PERSONALIZADOS POR ROL
---------------------------------------------------------------------
 DRF llama a has_permission() ANTES de ejecutar la vista. Si retorna
 False responde 403 Forbidden; si no se envió token responde 401.

 request.user lo arma JWTAuthentication a partir del token (verifica
 la firma y la expiración, y busca al usuario por su user_id).
 Aquí se revisa el rol de ese usuario.
=====================================================================
"""

from rest_framework.permissions import SAFE_METHODS, BasePermission


class EsOrganizador(BasePermission):
    """Solo usuarios con rol ORGANIZADOR."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == "ORGANIZADOR"


class EsEspectador(BasePermission):
    """Solo usuarios con rol ESPECTADOR."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == "ESPECTADOR"


class EsOrganizadorOSoloLectura(BasePermission):
    """
    Catálogo:
      - GET (lectura) -> público, cualquiera puede ver.
      - POST / PUT / PATCH / DELETE -> solo ORGANIZADOR.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return EsOrganizador().has_permission(request, view)
