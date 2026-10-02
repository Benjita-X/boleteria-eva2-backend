# 🎫 Boletería API — Venta de Entradas para Eventos y Conciertos

**EVA-2 Desarrollo Backend** · Proyecto 3
Django REST Framework + PostgreSQL + JWT + django-filter + Swagger

## Estructura

```
boleteria/   configuración (settings, urls, footer del alumno)
usuarios/    Usuario con rol, login JWT con claim de rol, permisos por rol
eventos/     Recinto, Evento, Sector (catálogo) + filtros
compras/     Carro (1 a 1), ItemCarro, Compra (estados), Ticket (UUID)
  services.py  lógica de pago, stock y cambio de estado
  signals.py   crea el carro al crear un usuario
templates/   página base con footer y Swagger con footer
```

## Cómo ejecutar

```bash
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py cargar_demo
python manage.py runserver
```
(o doble clic en `iniciar.bat`)

- Inicio: http://127.0.0.1:8000/
- Swagger: http://127.0.0.1:8000/api/docs/
- Tests: `python manage.py test`

### Usuarios de prueba

| Usuario | Rol | Contraseña |
|---|---|---|
| organizador1 | ORGANIZADOR | `Organiza.Demo.2026` |
| espectador1 / espectador2 | ESPECTADOR | `Espectador.Demo.2026` |
| admin | superusuario (/admin/) | `Admin.Demo.2026` |

## Endpoints

| Rol | Método | Endpoint |
|---|---|---|
| Público | POST | `/api/auth/login/` · `/api/auth/refresh/` |
| Público | GET | `/api/eventos/` · `/api/eventos/{id}/sectores/` |
| Autenticado | POST | `/api/auth/logout/` |
| Espectador | GET / POST / DELETE | `/api/carro-tickets/` |
| Espectador | POST | `/api/compras/pagar/` |
| Espectador | GET | `/api/mis-entradas/` |
| Organizador | POST / PUT / DELETE | `/api/eventos/` · `/api/sectores/` · `/api/recintos/` |
| Organizador | GET | `/api/compras/` |
| Organizador | PATCH | `/api/compras/{id}/estado/` |

## Filtros

```
/api/eventos/?artista=bunkers
/api/eventos/?ciudad=santiago
/api/eventos/?fecha_desde=2026-11-01&fecha_hasta=2026-12-31
/api/eventos/?precio_min=20000&precio_max=60000
/api/compras/?estado=PAGADO
```
