"""
=====================================================================
 VISTAS DE AUTENTICACIÓN
---------------------------------------------------------------------
   POST /api/auth/login/     -> devuelve access + refresh (con rol)
   POST /api/auth/refresh/   -> renueva el access usando el refresh
   POST /api/auth/logout/    -> invalida el refresh (blacklist)
=====================================================================
"""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import LogoutSerializer, TokenConRolSerializer


class LoginView(TokenObtainPairView):
    """Login JWT: usa el serializer que agrega el claim "rol" al token."""

    serializer_class = TokenConRolSerializer
    permission_classes = [AllowAny]


class LogoutView(APIView):
    """
    -----------------------------------------------------------------
    LOGOUT con JWT
    El servidor no guarda sesiones, así que el refresh se agrega a la
    lista negra (tabla token_blacklist) y ya no sirve para pedir más
    access tokens.
    El logout NO toca el carro: el carro vive en PostgreSQL ligado al
    usuario, por eso al volver a iniciar sesión los ítems siguen ahí.
    -----------------------------------------------------------------
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(request=LogoutSerializer, responses={205: None})
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            RefreshToken(serializer.validated_data["refresh"]).blacklist()
        except TokenError:
            return Response({"detail": "Token inválido."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_205_RESET_CONTENT)
