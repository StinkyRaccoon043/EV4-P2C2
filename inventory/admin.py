
from django.contrib import admin

from .models import (
    Equipment,
    Persona,
    Terreno,
    Vivienda,
    PuntoAcceso,
    ParticipacionVivienda,
)


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):

    list_display = (
        "rut",
        "nombre",
        "apellido",
        "email",
        "activo",
        "usuario",
    )

    search_fields = (
        "rut",
        "nombre",
        "apellido",
        "email",
        "usuario__username",
    )

    list_filter = ("activo",)


@admin.register(Terreno)
class TerrenoAdmin(admin.ModelAdmin):

    list_display = (
        "nombre",
        "direccion",
        "administrador",
        "activo",
    )

    search_fields = ("nombre", "direccion")
    list_filter = ("activo",)


@admin.register(Vivienda)
class ViviendaAdmin(admin.ModelAdmin):

    list_display = (
        "codigo_unidad",
        "direccion_interna",
        "terreno",
    )

    search_fields = ("codigo_unidad", "direccion_interna")


@admin.register(PuntoAcceso)
class PuntoAccesoAdmin(admin.ModelAdmin):

    list_display = (
        "codigo",
        "nombre",
        "tipo",
        "alcance",
        "terreno",
        "activo",
    )

    list_filter = ("tipo", "alcance", "activo")
    search_fields = ("codigo", "nombre")


@admin.register(ParticipacionVivienda)
class ParticipacionViviendaAdmin(admin.ModelAdmin):

    list_display = (
        "persona",
        "vivienda",
        "rol",
        "activa",
        "fecha_inicio",
        "fecha_fin",
    )

    list_filter = ("rol", "activa")
    search_fields = ("persona__rut", "vivienda__codigo_unidad")


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):

    list_display = ("code", "name", "is_available")
