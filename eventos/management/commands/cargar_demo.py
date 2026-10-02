"""
=====================================================================
 COMANDO: python manage.py cargar_demo
 Crea usuarios, recintos, eventos y sectores de prueba.
 El sector "Palco" tiene solo 2 entradas para mostrar el rechazo
 por stock insuficiente.
=====================================================================
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from eventos.models import Evento, Recinto, Sector
from usuarios.models import Usuario

# Credenciales SOLO de prueba (entorno local)
USUARIOS = [
    ("admin", "Admin.Demo.2026", "ORGANIZADOR"),
    ("organizador1", "Organiza.Demo.2026", "ORGANIZADOR"),
    ("espectador1", "Espectador.Demo.2026", "ESPECTADOR"),
    ("espectador2", "Espectador.Demo.2026", "ESPECTADOR"),
]


class Command(BaseCommand):
    help = "Carga datos de prueba."

    def handle(self, *args, **options):
        if Usuario.objects.filter(username="organizador1").exists():
            self.stdout.write("Los datos de prueba ya estaban cargados.")
            return

        for username, password, rol in USUARIOS:
            user = Usuario.objects.create_user(username=username, password=password, rol=rol)
            if username == "admin":
                user.is_staff = user.is_superuser = True
                user.save()

        organizador = Usuario.objects.get(username="organizador1")
        estadio = Recinto.objects.create(nombre="Estadio Nacional", direccion="Av. Grecia 2001", ciudad="Santiago")
        arena = Recinto.objects.create(nombre="Movistar Arena", direccion="Av. Beaucheff 1204", ciudad="Santiago")

        ahora = timezone.now()
        e1 = Evento.objects.create(nombre="Gira Aniversario", artista="Los Bunkers", recinto=estadio,
                                   organizador=organizador, fecha_hora=ahora + timedelta(days=45))
        e2 = Evento.objects.create(nombre="Noche de Rock", artista="Chancho en Piedra", recinto=arena,
                                   organizador=organizador, fecha_hora=ahora + timedelta(days=60))

        Sector.objects.create(evento=e1, nombre="Cancha General", precio=35000, stock=500)
        Sector.objects.create(evento=e1, nombre="VIP", precio=90000, stock=100)
        Sector.objects.create(evento=e2, nombre="Cancha", precio=30000, stock=300)
        Sector.objects.create(evento=e2, nombre="Palco", precio=120000, stock=2)

        self.stdout.write(self.style.SUCCESS("Datos de prueba cargados:"))
        for username, password, rol in USUARIOS:
            self.stdout.write(f"  {username:<14} {rol:<12} {password}")
