from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from inventory.views import EquipmentViewSet

router = DefaultRouter()
router.register("equipos", EquipmentViewSet, 
basename="Equipment")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]