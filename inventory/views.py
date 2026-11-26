
from django.db import IntegrityError, transaction
from django.db.models import Q

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import (
    Equipment,
    Persona,
    Vivienda,
    Terreno,
    PuntoAcceso,
    ParticipacionVivienda,
)

from .serializers import (
    EquipmentSerializer,
    PersonaSerializer,
    ViviendaSerializer,
    TerrenoSerializer,
    PuntoAccesoSerializer,
    AsignarPersonaSerializer,
    ParticipacionViviendaSerializer,
)


# --------------------------------------------------
# FUNCIONES DE APOYO PARA LOS PERMISOS
# --------------------------------------------------

def obtener_persona_activa(usuario):

    return Persona.objects.filter(
        usuario=usuario,
        activo=True,
    ).first()


def exigir_persona_activa(usuario):

    persona = obtener_persona_activa(usuario)

    if persona is None:
        raise PermissionDenied(
            "El usuario no tiene una persona activa vinculada."
        )

    return persona


# --------------------------------------------------
# EQUIPOS
# --------------------------------------------------

class EquipmentViewSet(ModelViewSet):

    queryset = Equipment.objects.order_by("id")
    serializer_class = EquipmentSerializer


# --------------------------------------------------
# PERSONAS
# --------------------------------------------------

class PersonaViewSet(ModelViewSet):

    queryset = Persona.objects.order_by("id")
    serializer_class = PersonaSerializer

    def get_queryset(self):

        usuario = self.request.user

        if usuario.is_superuser:
            return Persona.objects.order_by("id")

        persona = obtener_persona_activa(usuario)

        if persona is None:
            return Persona.objects.none()

        return Persona.objects.filter(
            Q(pk=persona.pk)
            | Q(viviendas__terreno__administrador=persona)
            | Q(
                participaciones__vivienda__terreno__administrador=persona
            )
        ).distinct().order_by("id")


# --------------------------------------------------
# VIVIENDAS
# --------------------------------------------------

class ViviendaViewSet(ModelViewSet):

    queryset = Vivienda.objects.select_related(
        "terreno",
        "terreno__administrador",
    ).prefetch_related(
        "propietarios"
    ).order_by("id")

    serializer_class = ViviendaSerializer

    def get_queryset(self):

        usuario = self.request.user

        queryset = super().get_queryset()

        if usuario.is_superuser:
            return queryset

        return queryset.filter(
            terreno__administrador__usuario=usuario,
            terreno__administrador__activo=True,
            terreno__activo=True,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="asignar-persona",
        serializer_class=AsignarPersonaSerializer,
    )
    def asignar_persona(self, request, pk=None):

        vivienda = self.get_object()

        entrada = self.get_serializer(data=request.data)

        entrada.is_valid(raise_exception=True)

        persona = entrada.validated_data["persona"]
        rol = entrada.validated_data["rol"]

        fecha_inicio = entrada.validated_data.get(
            "fecha_inicio"
        )

        try:

            with transaction.atomic():

                participacion = ParticipacionVivienda.objects.create(
                    persona=persona,
                    vivienda=vivienda,
                    rol=rol,
                    **(
                        {"fecha_inicio": fecha_inicio}
                        if fecha_inicio else {}
                    )
                )

                # Sincronizar la relación anterior de propietarios.

                if rol in [
                    ParticipacionVivienda.Rol.PROPIETARIO,
                    ParticipacionVivienda.Rol.PROPIETARIO_ADMINISTRADOR,
                ]:

                    vivienda.propietarios.add(persona)

        except IntegrityError:

            return Response(
                {
                    "error": (
                        "No se pudo realizar la asignación. "
                        "La persona ya tiene una participación activa "
                        "o la vivienda ya tiene un administrador activo."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        resultado = ParticipacionViviendaSerializer(
            participacion
        )

        return Response(
            resultado.data,
            status=status.HTTP_201_CREATED
        )


# --------------------------------------------------
# TERRENOS
# --------------------------------------------------

class TerrenoViewSet(ModelViewSet):

    queryset = Terreno.objects.select_related(
        "administrador",
        "administrador__usuario",
    ).order_by("id")

    serializer_class = TerrenoSerializer

    def get_queryset(self):

        usuario = self.request.user

        queryset = super().get_queryset()

        if usuario.is_superuser:
            return queryset

        return queryset.filter(
            administrador__usuario=usuario,
            administrador__activo=True,
        )

    def perform_create(self, serializer):

        if self.request.user.is_superuser:
            serializer.save()

        else:

            persona = exigir_persona_activa(
                self.request.user
            )

            serializer.save(
                administrador=persona
            )

    def perform_update(self, serializer):

        if self.request.user.is_superuser:
            serializer.save()

        else:

            persona = exigir_persona_activa(
                self.request.user
            )

            serializer.save(
                administrador=persona
            )


# --------------------------------------------------
# PUNTOS DE ACCESO
# --------------------------------------------------

class PuntoAccesoViewSet(ModelViewSet):

    queryset = PuntoAcceso.objects.select_related(
        "terreno",
        "terreno__administrador",
        "vivienda",
    ).order_by("id")

    serializer_class = PuntoAccesoSerializer

    def get_queryset(self):

        usuario = self.request.user

        queryset = super().get_queryset()

        if usuario.is_superuser:
            return queryset

        return queryset.filter(
            terreno__administrador__usuario=usuario,
            terreno__administrador__activo=True,
            terreno__activo=True,
        )
