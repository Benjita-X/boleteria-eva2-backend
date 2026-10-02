"""Registro de carros, compras y tickets en el panel /admin/."""

from django.contrib import admin

from .models import Carro, Compra, ItemCarro, Ticket

admin.site.register(Carro)
admin.site.register(ItemCarro)
admin.site.register(Compra)
admin.site.register(Ticket)
