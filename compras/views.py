"""
=====================================================================
 VISTAS DE COMPRAS
---------------------------------------------------------------------
   ESPECTADOR   GET/POST/DELETE /api/carro-tickets/
                POST /api/compras/pagar/
                GET  /api/mis-entradas/
   ORGANIZADOR  GET   /api/compras/              (consultar ventas)
                PATCH /api/compras/{id}/estado/
=====================================================================
"""

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from usuarios.permissions import EsEspectador, EsOrganizador

from . import services
from .models import Compra, ItemCarro, Ticket
from .serializers import CambioEstadoSerializer, CarroSerializer, CompraSerializer, ItemCarroSerializer, TicketSerializer


class CarroView(APIView):
    """
    -----------------------------------------------------------------
    /api/carro-tickets/
      GET    -> ver mi carro. Se busca con request.user (el usuario del
                token), por eso es el mismo carro aunque haga logout o
                entre desde otro dispositivo.
      POST   -> agregar {"sector": id, "cantidad": n}. Si el sector ya
                estaba, se suma la cantidad (no se duplica).
      DELETE -> vaciar el carro, o quitar un sector con ?sector=id
    -----------------------------------------------------------------
    """

    permission_classes = [EsEspectador]

    @extend_schema(responses=CarroSerializer)
    def get(self, request):
        return Response(CarroSerializer(request.user.carro).data)

    @extend_schema(request=ItemCarroSerializer, responses=CarroSerializer)
    def post(self, request):
        serializer = ItemCarroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sector = serializer.validated_data["sector"]
        cantidad = serializer.validated_data.get("cantidad", 1)

        item, creado = ItemCarro.objects.get_or_create(
            carro=request.user.carro, sector=sector, defaults={"cantidad": cantidad}
        )
        if not creado:
            item.cantidad += cantidad
            item.save()

        return Response(CarroSerializer(request.user.carro).data, status=status.HTTP_201_CREATED)

    @extend_schema(parameters=[OpenApiParameter("sector", int, required=False)], responses={204: None})
    def delete(self, request):
        items = request.user.carro.items.all()
        if request.query_params.get("sector"):
            items = items.filter(sector_id=request.query_params["sector"])
        items.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PagarView(APIView):
    """
    POST /api/compras/pagar/
    Convierte el carro en una Compra PAGADA (ver services.pagar_carro).
    Si no hay stock suficiente responde 400 y no se guarda nada.
    """

    permission_classes = [EsEspectador]

    @extend_schema(request=None, responses=CompraSerializer)
    def post(self, request):
        try:
            compra = services.pagar_carro(request.user)
        except services.ErrorCompra as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(CompraSerializer(compra).data, status=status.HTTP_201_CREATED)


class MisEntradasView(generics.ListAPIView):
    """GET /api/mis-entradas/ -> tickets (UUID) del usuario del token."""

    queryset = Ticket.objects.none()  # solo para que Swagger sepa el modelo
    serializer_class = TicketSerializer
    permission_classes = [EsEspectador]

    def get_queryset(self):
        return Ticket.objects.filter(compra__comprador=self.request.user)


class CompraViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    ORGANIZADOR:
      GET   /api/compras/              -> todas las ventas (filtro ?estado=PAGADO)
      PATCH /api/compras/{id}/estado/  -> {"estado": "ENTREGADO" | "CANCELADO"}
    """

    queryset = Compra.objects.all().order_by("-fecha")
    serializer_class = CompraSerializer
    permission_classes = [EsOrganizador]
    filterset_fields = ["estado"]

    @extend_schema(request=CambioEstadoSerializer, responses=CompraSerializer)
    @action(detail=True, methods=["patch"])
    def estado(self, request, pk=None):
        compra = self.get_object()
        serializer = CambioEstadoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            services.cambiar_estado(compra, serializer.validated_data["estado"])
        except services.ErrorCompra as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(CompraSerializer(compra).data)
