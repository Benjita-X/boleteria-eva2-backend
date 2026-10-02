"""
=====================================================================
 SERIALIZERS DE LA APP "compras"
=====================================================================
"""

from rest_framework import serializers

from .models import Carro, Compra, ItemCarro, Ticket


class ItemCarroSerializer(serializers.ModelSerializer):
    sector_nombre = serializers.CharField(source="sector.__str__", read_only=True)
    precio = serializers.IntegerField(source="sector.precio", read_only=True)

    class Meta:
        model = ItemCarro
        fields = ["id", "sector", "sector_nombre", "precio", "cantidad"]
        extra_kwargs = {"cantidad": {"min_value": 1}}


class CarroSerializer(serializers.ModelSerializer):
    items = ItemCarroSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Carro
        fields = ["id", "items", "total"]

    def get_total(self, carro) -> int:
        return sum(item.sector.precio * item.cantidad for item in carro.items.all())


class TicketSerializer(serializers.ModelSerializer):
    sector_nombre = serializers.CharField(source="sector.__str__", read_only=True)

    class Meta:
        model = Ticket
        fields = ["codigo", "compra", "sector", "sector_nombre", "precio"]


class CompraSerializer(serializers.ModelSerializer):
    comprador = serializers.CharField(source="comprador.username", read_only=True)
    tickets = TicketSerializer(many=True, read_only=True)

    class Meta:
        model = Compra
        fields = ["id", "comprador", "estado", "total", "fecha", "tickets"]


class CambioEstadoSerializer(serializers.Serializer):
    estado = serializers.ChoiceField(choices=Compra.Estado.choices)
