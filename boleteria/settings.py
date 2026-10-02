"""
=====================================================================
 CONFIGURACIÓN DEL PROYECTO "boleteria"
 Plataforma de venta de entradas para eventos y conciertos (EVA-2).
---------------------------------------------------------------------
 Lógica general:
   - Motor de BD: PostgreSQL (django.db.backends.postgresql).
   - Autenticación: JWT (djangorestframework-simplejwt) con claims
     de rol personalizados.
   - Documentación automática: drf-spectacular (Swagger / OpenAPI).
   - Filtros: django-filter aplicado por defecto a todos los endpoints.
=====================================================================
"""

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

# ---------------------------------------------------------------------
# Rutas base y carga del archivo .env
#   Las claves y datos locales se escriben en el .env (no en el código).
# ---------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# ---------------------------------------------------------------------
# Seguridad básica
#   SECRET_KEY firma los tokens JWT. DEBUG=True solo para desarrollo.
# ---------------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY") or "django-insecure-clave-de-desarrollo"
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# ---------------------------------------------------------------------
# Aplicaciones instaladas
#   - Apps de Django
#   - Librerías de terceros (DRF, JWT, filtros, Swagger)
#   - Apps propias: usuarios, eventos, compras
# ---------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Terceros
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",  # permite invalidar refresh tokens en el logout
    "django_filters",
    "drf_spectacular",
    # Propias
    "usuarios.apps.UsuariosConfig",
    "eventos.apps.EventosConfig",
    "compras.apps.ComprasConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "boleteria.urls"

# ---------------------------------------------------------------------
# Plantillas
#   Se agrega la carpeta /templates del proyecto para la vista HTML
#   base y de Swagger (con el footer del alumno). El context processor
#   "datos_alumno" pasa Nombre, Sección y Año a TODAS las plantillas.
# ---------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "boleteria.context_processors.datos_alumno",
            ],
        },
    },
]

WSGI_APPLICATION = "boleteria.wsgi.application"

# ---------------------------------------------------------------------
# BASE DE DATOS: PostgreSQL (motor nativo, NO SQLite)
#   Los datos de conexión se leen del archivo .env.
# ---------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME") or "boleteria_db",
        "USER": os.getenv("DB_USER") or "postgres",
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST") or "127.0.0.1",
        "PORT": os.getenv("DB_PORT") or "5432",
    }
}

# ---------------------------------------------------------------------
# Modelo de usuario personalizado
#   Se reemplaza el User de Django por usuarios.Usuario, que agrega el
#   campo "rol" (ESPECTADOR / ORGANIZADOR).
# ---------------------------------------------------------------------
AUTH_USER_MODEL = "usuarios.Usuario"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------
# Internacionalización (Chile)
# ---------------------------------------------------------------------
LANGUAGE_CODE = "es-cl"
TIME_ZONE = "America/Santiago"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------
# DJANGO REST FRAMEWORK
#   - Autenticación por defecto: JWT en el header "Authorization: Bearer".
#   - Permiso por defecto: IsAuthenticated (seguro por defecto). Cada
#     vista abre explícitamente lo que es público (catálogo).
#   - Filtros por defecto: django-filter.
#   - Esquema: drf-spectacular para generar el OpenAPI.
# ---------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# ---------------------------------------------------------------------
# SIMPLE JWT
#   - ACCESS (30 min): se envía en cada petición.
#   - REFRESH (1 día): sirve para pedir un access nuevo.
#   - TOKEN_OBTAIN_SERIALIZER: serializer propio que agrega el claim
#     "rol" dentro del payload del token.
# ---------------------------------------------------------------------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "TOKEN_OBTAIN_SERIALIZER": "usuarios.serializers.TokenConRolSerializer",
}

# ---------------------------------------------------------------------
# DATOS DEL ALUMNO (se muestran en el footer). Se completan en el .env
# ---------------------------------------------------------------------
ALUMNO = {
    "nombre": os.getenv("ALUMNO_NOMBRE", ""),
    "seccion": os.getenv("ALUMNO_SECCION", ""),
    "anio": os.getenv("ALUMNO_ANIO", ""),
}

# ---------------------------------------------------------------------
# DRF-SPECTACULAR (Swagger / OpenAPI en /api/docs/)
# ---------------------------------------------------------------------
SPECTACULAR_SETTINGS = {
    "TITLE": "API Boletería - Venta de Entradas para Eventos y Conciertos",
    "DESCRIPTION": "EVA-2 Desarrollo Backend · Django REST Framework + PostgreSQL + JWT",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}
