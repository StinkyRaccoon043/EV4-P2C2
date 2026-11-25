from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from inventory.views import EquipmentViewSet, PersonaViewSet, ViviendaViewSet

router = DefaultRouter()
router.register("equipos", EquipmentViewSet, basename="Equipment")
router.register("personas", PersonaViewSet, basename="persona")
router.register("viviendas", ViviendaViewSet, basename="vivienda")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]