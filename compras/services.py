"""
=====================================================================
 LÓGICA DE NEGOCIO: PAGO, STOCK Y ESTADOS
---------------------------------------------------------------------
 - @transaction.atomic: todo lo que pasa dentro de la función se
   guarda junto o NO se guarda nada (si hay un error se hace ROLLBACK).
   Así nunca queda una compra pagada sin descontar stock.
 - select_for_update(): bloquea la fila del sector en PostgreSQL
   mientras dura la transacción. Si dos personas compran la última
   entrada al mismo tiempo, la segunda espera y luego ve stock = 0,
   así no se vende dos veces la misma entrada.
=====================================================================
"""

from django.db import transaction
from django.db.models import F

from eventos.models import Sector

from .models import Compra, Ticket


class ErrorCompra(Exception):
    """Error de negocio (carro vacío, sin stock, estado inválido)."""


# Cambios de estado permitidos para el organizador
TRANSICIONES = {
    "PENDIENTE": ["CANCELADO"],
    "PAGADO": ["ENTREGADO", "CANCELADO"],
}


@transaction.atomic
def pagar_carro(usuario):
    """
    -----------------------------------------------------------------
    CHECKOUT + PAGO
    1) Crea la Compra (estado inicial PENDIENTE).
    2) Por cada ítem del carro:
         - bloquea el sector (select_for_update)
         - si no hay stock suficiente -> error -> ROLLBACK de todo
         - descuenta el stock
         - crea un Ticket (UUID) por cada entrada
    3) Guarda el total, pasa la compra a PAGADO y vacía el carro.
    -----------------------------------------------------------------
    """
    items = list(usuario.carro.items.all())
    if not items:
        raise ErrorCompra("El carro está vacío.")

    compra = Compra.objects.create(comprador=usuario)  # PENDIENTE
    total = 0

    for item in items:
        sector = Sector.objects.select_for_update().get(pk=item.sector_id)

        if sector.stock < item.cantidad:
            raise ErrorCompra(f"Stock insuficiente en {sector}: quedan {sector.stock}.")

        sector.stock -= item.cantidad
        sector.save()

        for _ in range(item.cantidad):
            Ticket.objects.create(compra=compra, sector=sector, precio=sector.precio)
        total += sector.precio * item.cantidad

    compra.total = total
    compra.estado = Compra.Estado.PAGADO
    compra.save()

    usuario.carro.items.all().delete()
    return compra


@transaction.atomic
def cambiar_estado(compra, nuevo_estado):
    """
    -----------------------------------------------------------------
    CAMBIO DE ESTADO (organizador)
    - Revisa que el cambio esté permitido en TRANSICIONES.
    - Si se CANCELA: devuelve al sector 1 entrada por cada ticket.
    -----------------------------------------------------------------
    """
    if nuevo_estado not in TRANSICIONES.get(compra.estado, []):
        raise ErrorCompra(f"No se puede pasar de {compra.estado} a {nuevo_estado}.")

    if nuevo_estado == Compra.Estado.CANCELADO:
        for ticket in compra.tickets.all():
            Sector.objects.filter(pk=ticket.sector_id).update(stock=F("stock") + 1)

    compra.estado = nuevo_estado
    compra.save()
    return compra
