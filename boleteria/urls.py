"""
=====================================================================
 URLS PRINCIPALES
---------------------------------------------------------------------
 - "/"           -> página HTML base con el footer del alumno
 - "/admin/"     -> panel de administración de Django
 - "/api/auth/"  -> login JWT, refresh y logout
 - "/api/..."    -> endpoints de la matriz de roles
 - "/api/docs/"  -> Swagger (documentación OpenAPI automática)
 La ruta "compras/pagar/" va ANTES del router para que "pagar" no se
 confunda con el {id} de una compra.
=====================================================================
"""

from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from compras.views import CarroView, CompraViewSet, MisEntradasView, PagarView
from eventos.views import EventoViewSet, RecintoViewSet, SectorViewSet

router = DefaultRouter()
router.register("eventos", EventoViewSet)
router.register("sectores", SectorViewSet)
router.register("recintos", RecintoViewSet)
router.register("compras", CompraViewSet)

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html")),
    path("admin/", admin.site.urls),
    path("api/auth/", include("usuarios.urls")),
    path("api/carro-tickets/", CarroView.as_view()),
    path("api/compras/pagar/", PagarView.as_view()),
    path("api/mis-entradas/", MisEntradasView.as_view()),
    path("api/", include(router.urls)),
    # Swagger / OpenAPI
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema", template_name="swagger_alumno.html")),
]
