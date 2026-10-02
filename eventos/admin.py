"""Registro del catálogo en el panel /admin/."""

from django.contrib import admin

from .models import Evento, Recinto, Sector

admin.site.register(Recinto)
admin.site.register(Evento)
admin.site.register(Sector)
