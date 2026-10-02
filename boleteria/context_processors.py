"""
=====================================================================
 CONTEXT PROCESSOR: datos_alumno
---------------------------------------------------------------------
 Django ejecuta esta función en cada render de plantilla y agrega la
 variable {{ alumno }} al contexto. Así el footer de TODAS las vistas
 HTML (home y API navegable de DRF) muestra Nombre, Sección y Año sin
 repetir código en cada vista.
=====================================================================
"""

from django.conf import settings


def datos_alumno(request):
    return {"alumno": settings.ALUMNO}
