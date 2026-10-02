"""
=====================================================================
 MODELOS DE LA APP "usuarios"
---------------------------------------------------------------------
 Se extiende AbstractUser (el usuario estándar de Django) agregando
 el campo "rol". Este rol viaja dentro del token JWT como claim y lo
 revisan las clases de permiso (usuarios/permissions.py).
=====================================================================
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    # CHOICES: el rol solo puede tomar uno de estos dos valores
    class Rol(models.TextChoices):
        ESPECTADOR = "ESPECTADOR", "Espectador"
        ORGANIZADOR = "ORGANIZADOR", "Organizador de Eventos"

    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.ESPECTADOR)

    def __str__(self):
        return f"{self.username} ({self.rol})"
