from rest_framework.viewsets import ModelViewSet
from .models import Equipment, Persona, Vivienda
from .serializers import EquipmentSerializer, PersonaSerializer, ViviendaSerializer

class EquipmentViewSet(ModelViewSet):
    queryset = Equipment.objects.order_by("id")
    serializer_class = EquipmentSerializer


class PersonaViewSet(ModelViewSet):
    queryset = Persona.objects.all()
    serializer_class = PersonaSerializer


class ViviendaViewSet(ModelViewSet):
    queryset = Vivienda.objects.all()
    serializer_class = ViviendaSerializer