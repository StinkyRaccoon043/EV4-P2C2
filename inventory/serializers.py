
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import (
    Equipment,
    Persona,
    Vivienda,
    Terreno,
    PuntoAcceso,
    ParticipacionVivienda,
)


class EquipmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Equipment
        fields = (
            "id",
            "code",
            "name",
            "is_available",
        )


class PersonaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Persona
        fields = [
            "id",
            "rut",
            "nombre",
            "apellido",
            "email",
            "telefono",
            "activo",
        ]


class ViviendaSerializer(serializers.ModelSerializer):

    terreno = serializers.PrimaryKeyRelatedField(
        queryset=Terreno.objects.all(),
        required=False,
        allow_null=True,
    )

    propietarios = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Persona.objects.filter(activo=True),
        required=False,
    )

    class Meta:
        model = Vivienda
        fields = [
            "id",
            "codigo_unidad",
            "direccion_interna",
            "terreno",
            "propietarios",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")

        if request and request.user.is_authenticated:
            if not request.user.is_superuser:

                terrenos = Terreno.objects.filter(
                    administrador__usuario=request.user,
                    administrador__activo=True,
                    activo=True,
                )

                self.fields["terreno"].queryset = terrenos
                self.fields["terreno"].required = True
                self.fields["terreno"].allow_null = False


class TerrenoSerializer(serializers.ModelSerializer):

    administrador = serializers.PrimaryKeyRelatedField(
        queryset=Persona.objects.filter(activo=True),
        required=True,
    )

    class Meta:
        model = Terreno
        fields = [
            "id",
            "nombre",
            "direccion",
            "administrador",
            "activo",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")

        if request and request.user.is_authenticated:
            if not request.user.is_superuser:

                self.fields["administrador"].queryset = (
                    Persona.objects.filter(
                        usuario=request.user,
                        activo=True,
                    )
                )

                # El administrador se asignará automáticamente
                # desde la vista.
                self.fields["administrador"].required = False


class PuntoAccesoSerializer(serializers.ModelSerializer):

    terreno = serializers.PrimaryKeyRelatedField(
        queryset=Terreno.objects.all()
    )

    vivienda = serializers.PrimaryKeyRelatedField(
        queryset=Vivienda.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = PuntoAcceso
        fields = [
            "id",
            "codigo",
            "nombre",
            "tipo",
            "alcance",
            "terreno",
            "vivienda",
            "activo",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")

        if request and request.user.is_authenticated:
            if not request.user.is_superuser:

                terrenos = Terreno.objects.filter(
                    administrador__usuario=request.user,
                    administrador__activo=True,
                    activo=True,
                )

                viviendas = Vivienda.objects.filter(
                    terreno__in=terrenos
                )

                self.fields["terreno"].queryset = terrenos
                self.fields["vivienda"].queryset = viviendas

    def validate(self, attrs):

        punto = self.instance or PuntoAcceso()

        for campo, valor in attrs.items():
            setattr(punto, campo, valor)

        try:
            punto.clean()

        except DjangoValidationError as error:

            if hasattr(error, "message_dict"):
                raise serializers.ValidationError(
                    error.message_dict
                )

            raise serializers.ValidationError(error.messages)

        return attrs


class AsignarPersonaSerializer(serializers.Serializer):

    persona = serializers.PrimaryKeyRelatedField(
        queryset=Persona.objects.filter(activo=True)
    )

    rol = serializers.ChoiceField(
        choices=ParticipacionVivienda.Rol.choices
    )

    fecha_inicio = serializers.DateField(
        required=False
    )


class ParticipacionViviendaSerializer(serializers.ModelSerializer):

    class Meta:
        model = ParticipacionVivienda

        fields = [
            "id",
            "persona",
            "vivienda",
            "rol",
            "activa",
            "fecha_inicio",
            "fecha_fin",
        ]

        read_only_fields = fields
