"""
=====================================================================
 MODELOS DE LA APP "compras"
---------------------------------------------------------------------
 Relaciones:

   Usuario 1 ──── 1 Carro 1 ──── N ItemCarro N ──── 1 Sector
   Usuario 1 ──── N Compra 1 ──── N Ticket   N ──── 1 Sector

 Flujo:
   1) El espectador agrega sectores a su Carro (NO se toca el stock).
   2) Pagar: se crea la Compra, se valida y descuenta el stock, se
      emite un Ticket con UUID por cada entrada y queda PAGADO.
   3) El organizador cambia la compra a ENTREGADO o CANCELADO
      (al cancelar se repone el stock).
=====================================================================
"""

import uuid

from django.conf import settings
from django.db import models

from eventos.models import Sector


class Carro(models.Model):
    """
    -----------------------------------------------------------------
    CARRO PERSISTENTE ("Reserva Temporal de Entradas")
    - OneToOneField: cada usuario tiene UN solo carro (relación 1 a 1).
    - Está guardado en PostgreSQL (no en la sesión ni en el frontend),
      por eso los ítems se mantienen después del logout o al entrar
      desde otro dispositivo.
    - Se crea automáticamente al crear el usuario (ver signals.py).
    -----------------------------------------------------------------
    """

    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="carro")

    def __str__(self):
        return f"Carro de {self.usuario.username}"


class ItemCarro(models.Model):
    """
    Una línea del carro: sector + cantidad de entradas.
    unique_together evita duplicados: el mismo sector no puede estar
    dos veces en el mismo carro (si se vuelve a agregar, se suma).
    """

    carro = models.ForeignKey(Carro, on_delete=models.CASCADE, related_name="items")
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ["carro", "sector"]

    def __str__(self):
        return f"{self.cantidad} x {self.sector}"


class Compra(models.Model):
    """
    -----------------------------------------------------------------
    ORDEN / TRANSACCIÓN (registro histórico de la compra)
    estado usa CHOICES:
        PENDIENTE -> PAGADO -> ENTREGADO
                       └────-> CANCELADO (se repone el stock)
    -----------------------------------------------------------------
    """

    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        PAGADO = "PAGADO", "Pagado"
        ENTREGADO = "ENTREGADO", "Entregado"
        CANCELADO = "CANCELADO", "Cancelado"

    comprador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="compras")
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.PENDIENTE)
    total = models.PositiveIntegerField(default=0)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Compra #{self.pk} - {self.comprador.username} - {self.estado}"


class Ticket(models.Model):
    """
    -----------------------------------------------------------------
    ENTRADA EMITIDA con código UUID único
    - default=uuid.uuid4 genera un código aleatorio imposible de adivinar.
    - unique=True: la BD no permite dos tickets con el mismo código.
    - precio: copia del precio al momento de pagar (si después cambia
      el precio del sector, la compra no se ve afectada).
    - Se crea UN ticket por cada entrada (3 VIP = 3 tickets).
    -----------------------------------------------------------------
    """

    codigo = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name="tickets")
    sector = models.ForeignKey(Sector, on_delete=models.PROTECT)
    precio = models.PositiveIntegerField()

    def __str__(self):
        return str(self.codigo)
