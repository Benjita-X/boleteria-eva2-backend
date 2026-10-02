"""
=====================================================================
 VISTAS DEL CATÁLOGO (app "eventos")
---------------------------------------------------------------------
   PÚBLICO      GET /api/eventos/
                GET /api/eventos/{id}/sectores/
   ORGANIZADOR  POST/PUT/DELETE /api/eventos/
                POST/PUT/DELETE /api/sectores/ y /api/recintos/

 ModelViewSet entrega listar, ver, crear, editar y borrar en una sola
 clase; el router (boleteria/urls.py) genera las URLs.
=====================================================================
"""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from usuarios.permissions import EsOrganizadorOSoloLectura

from .filters import EventoFilter
from .models import Evento, Recinto, Sector
from .serializers import EventoSerializer, RecintoSerializer, SectorSerializer


class EventoViewSet(viewsets.ModelViewSet):
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    permission_classes = [EsOrganizadorOSoloLectura]
    filterset_class = EventoFilter  # filtros de django-filter

    def perform_create(self, serializer):
        # El organizador es el usuario dueño del token
        serializer.save(organizador=self.request.user)

    @action(detail=True, methods=["get"], permission_classes=[AllowAny])
    def sectores(self, request, pk=None):
        """GET /api/eventos/{id}/sectores/ -> sectores con precio y stock (público)."""
        evento = self.get_object()
        return Response(SectorSerializer(evento.sectores.all(), many=True).data)


class SectorViewSet(viewsets.ModelViewSet):
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer
    permission_classes = [EsOrganizadorOSoloLectura]
    filterset_fields = ["evento"]


class RecintoViewSet(viewsets.ModelViewSet):
    queryset = Recinto.objects.all()
    serializer_class = RecintoSerializer
    permission_classes = [EsOrganizadorOSoloLectura]
    filterset_fields = ["ciudad"]
