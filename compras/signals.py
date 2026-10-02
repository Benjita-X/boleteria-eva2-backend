"""
=====================================================================
 SEÑALES (signals) DE LA APP "compras"
---------------------------------------------------------------------
 post_save se ejecuta cada vez que se guarda un Usuario. Si es un
 usuario NUEVO (created=True) se le crea su Carro (relación 1 a 1).
 Se activa en ComprasConfig.ready() (apps.py).
=====================================================================
"""

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Carro


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def crear_carro(sender, instance, created, **kwargs):
    if created:
        Carro.objects.create(usuario=instance)
