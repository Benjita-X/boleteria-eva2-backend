"""
=====================================================================
 MODELOS DE LA APP "eventos" (CATÁLOGO)
---------------------------------------------------------------------
 Relaciones:

   Recinto 1 ──── N Evento 1 ──── N Sector

 - Un Recinto (ej. Movistar Arena) aloja muchos Eventos.
 - Un Evento tiene muchos Sectores (Cancha, VIP, Tribuna...).
 - El PRECIO y el STOCK de entradas están en el Sector, porque cada
   localidad tiene su propio precio y cantidad de entradas.
=====================================================================
"""

from django.conf import settings
from django.db import models


class Recinto(models.Model):
    """Lugar donde se realiza el evento."""

    nombre = models.CharField(max_length=150)
    direccion = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Evento(models.Model):
    """
    Evento o concierto.
    - recinto: FK a Recinto. PROTECT impide borrar un recinto con eventos.
    - organizador: FK al Usuario (Organizador) que lo creó.
    """

    nombre = models.CharField(max_length=200)
    artista = models.CharField(max_length=150)
    fecha_hora = models.DateTimeField()
    recinto = models.ForeignKey(Recinto, on_delete=models.PROTECT, related_name="eventos")
    organizador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="eventos")

    def __str__(self):
        return f"{self.nombre} - {self.artista}"


class Sector(models.Model):
    """
    Sector / Localidad de un evento (ej. VIP, Cancha General).
    - precio: precio actual de la entrada.
    - stock: entradas disponibles. SOLO se descuenta cuando una compra
      pasa a PAGADO y se repone si la compra se CANCELA.
      PositiveIntegerField impide que quede negativo.
    """

    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name="sectores")
    nombre = models.CharField(max_length=100)
    precio = models.PositiveIntegerField(help_text="Precio en pesos (CLP)")
    stock = models.PositiveIntegerField(help_text="Entradas disponibles")

    def __str__(self):
        return f"{self.evento.nombre} - {self.nombre}"
