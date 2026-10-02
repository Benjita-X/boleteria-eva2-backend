"""
=====================================================================
 TESTS DEL FLUJO COMPLETO  ->  python manage.py test
 Django crea una BD PostgreSQL temporal, ejecuta las pruebas y la borra.
=====================================================================
"""

from datetime import timedelta

from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from eventos.models import Evento, Recinto, Sector
from usuarios.models import Usuario

from .models import Compra

CLAVE = "Clave.Segura.123"


class FlujoTests(APITestCase):
    def setUp(self):
        self.org = Usuario.objects.create_user("org", password=CLAVE, rol="ORGANIZADOR")
        Usuario.objects.create_user("esp1", password=CLAVE)
        Usuario.objects.create_user("esp2", password=CLAVE)
        recinto = Recinto.objects.create(nombre="Arena", direccion="X", ciudad="Santiago")
        self.evento = Evento.objects.create(nombre="Concierto", artista="Banda", recinto=recinto,
                                            organizador=self.org, fecha_hora=timezone.now() + timedelta(days=30))
        self.vip = Sector.objects.create(evento=self.evento, nombre="VIP", precio=90000, stock=5)

    def login(self, username):
        r = self.client.post("/api/auth/login/", {"username": username, "password": CLAVE})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {r.data['access']}")
        return r.data

    def agregar(self, cantidad):
        return self.client.post("/api/carro-tickets/", {"sector": self.vip.id, "cantidad": cantidad})

    def test_token_tiene_claim_de_rol(self):
        data = self.login("org")
        self.assertEqual(AccessToken(data["access"])["rol"], "ORGANIZADOR")

    def test_permisos_por_rol(self):
        datos = {"nombre": "Otro", "artista": "A", "recinto": self.evento.recinto_id,
                 "fecha_hora": timezone.now().isoformat()}
        self.assertEqual(self.client.get("/api/eventos/").status_code, 200)       # público
        self.assertEqual(self.client.post("/api/eventos/", datos).status_code, 401)  # sin token
        self.login("esp1")
        self.assertEqual(self.client.post("/api/eventos/", datos).status_code, 403)  # espectador
        self.login("org")
        self.assertEqual(self.client.post("/api/eventos/", datos).status_code, 201)  # organizador

    def test_carro_persiste_despues_del_logout(self):
        tokens = self.login("esp1")
        self.agregar(2)
        self.agregar(1)  # mismo sector: se suma, no se duplica
        self.client.post("/api/auth/logout/", {"refresh": tokens["refresh"]})
        self.login("esp1")
        items = self.client.get("/api/carro-tickets/").data["items"]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["cantidad"], 3)
        self.vip.refresh_from_db()
        self.assertEqual(self.vip.stock, 5)  # agregar al carro NO descuenta stock

    def test_pagar_descuenta_stock_y_crea_tickets_uuid(self):
        self.login("esp1")
        self.agregar(3)
        r = self.client.post("/api/compras/pagar/")
        self.assertEqual(r.data["estado"], "PAGADO")
        self.assertEqual(len({t["codigo"] for t in r.data["tickets"]}), 3)
        self.vip.refresh_from_db()
        self.assertEqual(self.vip.stock, 2)

    def test_stock_insuficiente_rechaza_la_compra(self):
        self.login("esp1")
        self.agregar(6)
        r = self.client.post("/api/compras/pagar/")
        self.assertEqual(r.status_code, 400)
        self.vip.refresh_from_db()
        self.assertEqual(self.vip.stock, 5)                 # no se descontó nada
        self.assertEqual(Compra.objects.count(), 0)         # rollback: no quedó la compra

    def test_cancelar_repone_stock(self):
        self.login("esp1")
        self.agregar(2)
        compra_id = self.client.post("/api/compras/pagar/").data["id"]
        self.login("org")
        r = self.client.patch(f"/api/compras/{compra_id}/estado/", {"estado": "CANCELADO"})
        self.assertEqual(r.data["estado"], "CANCELADO")
        self.vip.refresh_from_db()
        self.assertEqual(self.vip.stock, 5)
        # no se puede cancelar dos veces
        r = self.client.patch(f"/api/compras/{compra_id}/estado/", {"estado": "CANCELADO"})
        self.assertEqual(r.status_code, 400)

    def test_filtro_por_precio(self):
        self.assertEqual(len(self.client.get("/api/eventos/?precio_min=80000").data), 1)
        self.assertEqual(len(self.client.get("/api/eventos/?precio_min=100000").data), 0)

    def test_swagger_y_footer(self):
        self.assertContains(self.client.get("/api/docs/"), "Sección:")
        self.assertContains(self.client.get("/"), "Sección:")
