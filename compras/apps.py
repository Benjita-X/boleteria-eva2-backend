from django.apps import AppConfig


class ComprasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "compras"

    def ready(self):
        # Importar el módulo registra los @receiver (crea el carro al crear usuario)
        from . import signals  # noqa: F401
