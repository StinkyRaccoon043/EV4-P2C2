
from django.contrib import admin
from django.urls import include, path

from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from inventory.views import (
    EquipmentViewSet,
    PersonaViewSet,
    ViviendaViewSet,
    TerrenoViewSet,
    PuntoAccesoViewSet,
)


# ROUTER

router = DefaultRouter()

router.register(
    "equipos",
    EquipmentViewSet,
    basename="equipo"
)

router.register(
    "personas",
    PersonaViewSet,
    basename="persona"
)

router.register(
    "viviendas",
    ViviendaViewSet,
    basename="vivienda"
)

router.register(
    "terrenos",
    TerrenoViewSet,
    basename="terreno"
)

router.register(
    "puntos-acceso",
    PuntoAccesoViewSet,
    basename="punto-acceso"
)


# URLS

urlpatterns = [

    path(
        "admin/",
        admin.site.urls
    ),

    # JWT: obtener Access y Refresh Token
    path(
        "api/token/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair"
    ),

    # JWT: renovar Access Token
    path(
        "api/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh"
    ),

    # JWT: verificar token
    path(
        "api/token/verify/",
        TokenVerifyView.as_view(),
        name="token_verify"
    ),

    # API principal
    path(
        "api/",
        include(router.urls)
    ),

]
