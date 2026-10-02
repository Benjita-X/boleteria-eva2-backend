"""
=====================================================================
 SERIALIZERS DE LA APP "usuarios"
=====================================================================
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class TokenConRolSerializer(TokenObtainPairSerializer):
    """
    -----------------------------------------------------------------
    TOKEN JWT CON CLAIMS PERSONALIZADOS
    -----------------------------------------------------------------
    simplejwt genera por defecto un payload con: token_type, exp, iat,
    jti y user_id. Aquí se sobrescribe get_token() para AGREGAR:
        - rol       -> "ESPECTADOR" u "ORGANIZADOR"
        - username
    Estos claims quedan firmados con la SECRET_KEY: el cliente puede
    leerlos, pero NO modificarlos sin invalidar la firma.

    validate() además devuelve el rol en la respuesta JSON del login.
    -----------------------------------------------------------------
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["rol"] = user.rol
        token["username"] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["rol"] = self.user.rol
        return data


class LogoutSerializer(serializers.Serializer):
    """Recibe el refresh token que se va a invalidar."""

    refresh = serializers.CharField()
