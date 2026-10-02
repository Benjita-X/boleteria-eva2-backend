"""
=====================================================================
 FILTROS (django-filter) DEL CATÁLOGO
---------------------------------------------------------------------
 Cada filtro convierte un parámetro de la URL en una condición del
 ORM (que termina siendo un WHERE en SQL). Ejemplos:

   /api/eventos/?artista=bunkers
   /api/eventos/?ciudad=santiago
   /api/eventos/?fecha_desde=2026-11-01&fecha_hasta=2026-12-31
   /api/eventos/?precio_min=20000&precio_max=60000
=====================================================================
"""

import django_filters

from .models import Evento


class EventoFilter(django_filters.FilterSet):
    # icontains = búsqueda parcial sin importar mayúsculas
    artista = django_filters.CharFilter(lookup_expr="icontains")
    ciudad = django_filters.CharFilter(field_name="recinto__ciudad", lookup_expr="icontains")

    # Rango de fechas
    fecha_desde = django_filters.DateFilter(field_name="fecha_hora", lookup_expr="date__gte")
    fecha_hasta = django_filters.DateFilter(field_name="fecha_hora", lookup_expr="date__lte")

    # Rango de precios (sobre los sectores del evento).
    # distinct=True evita que un evento aparezca repetido.
    precio_min = django_filters.NumberFilter(field_name="sectores__precio", lookup_expr="gte", distinct=True)
    precio_max = django_filters.NumberFilter(field_name="sectores__precio", lookup_expr="lte", distinct=True)

    class Meta:
        model = Evento
        fields = ["recinto"]
