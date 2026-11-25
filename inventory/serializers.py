from rest_framework import serializers
from .models import Equipment, Persona, Vivienda

class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = ("id", "code", "name", "is_available")


class PersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = ["id", "rut", "nombre", "apellido", "email", "telefono", "activo"]


class ViviendaSerializer(serializers.ModelSerializer):
    propietarios = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Persona.objects.all(),
        required=False,
    )

    class Meta:
        model = Vivienda
        fields = ["id", "codigo_unidad", "direccion_interna", "propietarios"]