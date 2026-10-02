"""
=====================================================================
 SERIALIZERS DEL CATÁLOGO
 Convierten los modelos a JSON (y validan el JSON que llega).
=====================================================================
"""

from rest_framework import serializers

from .models import Evento, Recinto, Sector


class RecintoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recinto
        fields = ["id", "nombre", "direccion", "ciudad"]


class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = ["id", "evento", "nombre", "precio", "stock"]


class EventoSerializer(serializers.ModelSerializer):
    """
    - organizador: solo lectura; se asigna en la vista con el usuario
      del token (no lo manda el cliente).
    - sectores: se muestran dentro del evento (solo lectura).
    """

    organizador = serializers.CharField(source="organizador.username", read_only=True)
    sectores = SectorSerializer(many=True, read_only=True)

    class Meta:
        model = Evento
        fields = ["id", "nombre", "artista", "fecha_hora", "recinto", "organizador", "sectores"]
