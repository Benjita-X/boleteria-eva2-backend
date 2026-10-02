"""Registro del usuario personalizado en el panel /admin/ (agrega el campo rol)."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ("username", "email", "rol", "is_staff", "is_active")
    list_filter = ("rol", "is_staff", "is_active")
    fieldsets = UserAdmin.fieldsets + (("Rol en la plataforma", {"fields": ("rol",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Rol en la plataforma", {"fields": ("rol",)}),)
