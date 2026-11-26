
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from .models import (
    Persona,
    Terreno,
    Vivienda,
    PuntoAcceso,
)


User = get_user_model()


# --------------------------------------------------
# PRUEBAS DE PERSONAS
# --------------------------------------------------

class PersonaApiTests(APITestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="test_persona",
            password="TestPassword123!"
        )

        self.client.force_authenticate(
            user=self.user
        )

    def test_create_person_and_reject_duplicate_rut(self):

        person = {
            "rut": "12345678-9",
            "nombre": "Ana",
            "apellido": "Perez",
            "email": "ana@example.com",
        }

        response = self.client.post(
            "/api/personas/",
            person,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            response.data["rut"],
            person["rut"]
        )

        duplicate = dict(
            person,
            email="otra@example.com"
        )

        response = self.client.post(
            "/api/personas/",
            duplicate,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )


# --------------------------------------------------
# PRUEBAS DE VIVIENDAS
# --------------------------------------------------

class ViviendaApiTests(APITestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="test_vivienda",
            password="TestPassword123!"
        )

        self.client.force_authenticate(
            user=self.user
        )

        self.administrador = Persona.objects.create(
            rut="99999999-9",
            nombre="Administrador",
            apellido="Prueba",
            email="admin@example.com",
            usuario=self.user,
        )

        self.terreno = Terreno.objects.create(
            nombre="Terreno de prueba",
            direccion="Direccion de prueba",
            administrador=self.administrador,
        )

    def test_create_and_update_owner_relationships(self):

        first_person = self.client.post(
            "/api/personas/",
            {
                "rut": "11111111-1",
                "nombre": "Ana",
                "apellido": "Perez",
                "email": "ana@example.com",
            },
            format="json",
        )

        second_person = self.client.post(
            "/api/personas/",
            {
                "rut": "22222222-2",
                "nombre": "Luis",
                "apellido": "Soto",
                "email": "luis@example.com",
            },
            format="json",
        )

        owner_ids = [
            first_person.data["id"],
            second_person.data["id"],
        ]

        created = self.client.post(
            "/api/viviendas/",
            {
                "codigo_unidad": "Depto 402",
                "direccion_interna": "Torre Norte, Piso 4",
                "terreno": self.terreno.id,
                "propietarios": owner_ids,
            },
            format="json",
        )

        self.assertEqual(
            created.status_code,
            status.HTTP_201_CREATED
        )

        self.assertCountEqual(
            created.data["propietarios"],
            owner_ids
        )

        updated = self.client.put(
            f"/api/viviendas/{created.data['id']}/",
            {
                "codigo_unidad": "Depto 402",
                "direccion_interna": "Torre Norte, Piso 5",
                "terreno": self.terreno.id,
                "propietarios": [owner_ids[0]],
            },
            format="json",
        )

        self.assertEqual(
            updated.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            updated.data["direccion_interna"],
            "Torre Norte, Piso 5"
        )

        self.assertEqual(
            updated.data["propietarios"],
            [owner_ids[0]]
        )


# --------------------------------------------------
# PRUEBAS DE AUTENTICACION JWT
# --------------------------------------------------

class JWTAuthenticationTests(APITestCase):

    def setUp(self):

        self.password = "TestPassword123!"

        self.user = User.objects.create_user(
            username="jwt_test",
            password=self.password
        )

    def test_api_requires_authentication(self):

        response = self.client.get(
            "/api/personas/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_obtain_jwt_tokens(self):

        response = self.client.post(
            "/api/token/",
            {
                "username": self.user.username,
                "password": self.password,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_refresh_jwt_token(self):

        login = self.client.post(
            "/api/token/",
            {
                "username": self.user.username,
                "password": self.password,
            },
            format="json"
        )

        refresh = login.data["refresh"]

        response = self.client.post(
            "/api/token/refresh/",
            {
                "refresh": refresh
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertIn("access", response.data)

    def test_authenticated_user_can_access_api(self):

        login = self.client.post(
            "/api/token/",
            {
                "username": self.user.username,
                "password": self.password,
            },
            format="json"
        )

        access = login.data["access"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access}"
        )

        response = self.client.get(
            "/api/personas/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )


# --------------------------------------------------
# PRUEBAS DE PERMISOS POR TERRENO
# --------------------------------------------------

class PermisosPorTerrenoApiTests(APITestCase):

    def setUp(self):

        # Usuario A: Sofía.

        self.user_a = User.objects.create_user(
            username="sofia_test",
            password="TestPassword123!"
        )

        self.persona_a = Persona.objects.create(
            rut="33333333-3",
            nombre="Sofia",
            apellido="Pizarro",
            email="sofia_test@example.com",
            usuario=self.user_a,
        )

        # Usuario B: otro administrador.

        self.user_b = User.objects.create_user(
            username="otro_admin",
            password="TestPassword123!"
        )

        self.persona_b = Persona.objects.create(
            rut="44444444-4",
            nombre="Carlos",
            apellido="Prueba",
            email="carlos_test@example.com",
            usuario=self.user_b,
        )

        # Terrenos independientes.

        self.terreno_a = Terreno.objects.create(
            nombre="Terreno Sofia",
            direccion="Direccion Sofia",
            administrador=self.persona_a,
        )

        self.terreno_b = Terreno.objects.create(
            nombre="Terreno Carlos",
            direccion="Direccion Carlos",
            administrador=self.persona_b,
        )

        # Viviendas independientes.

        self.vivienda_a = Vivienda.objects.create(
            codigo_unidad="SOFIA-101",
            direccion_interna="Casa Sofia",
            terreno=self.terreno_a,
        )

        self.vivienda_b = Vivienda.objects.create(
            codigo_unidad="CARLOS-101",
            direccion_interna="Casa Carlos",
            terreno=self.terreno_b,
        )

        # Persona propietaria relacionada con el terreno A.

        self.propietario_a = Persona.objects.create(
            rut="55555555-5",
            nombre="Ana",
            apellido="Propietaria",
            email="ana_propietaria@example.com",
        )

        self.vivienda_a.propietarios.add(
            self.propietario_a
        )

        # Puntos de acceso independientes.

        self.acceso_a = PuntoAcceso.objects.create(
            codigo="ACC-SOFIA",
            nombre="Porton Sofia",
            tipo=PuntoAcceso.Tipo.PORTON,
            alcance=PuntoAcceso.Alcance.COMUN,
            terreno=self.terreno_a,
        )

        self.acceso_b = PuntoAcceso.objects.create(
            codigo="ACC-CARLOS",
            nombre="Porton Carlos",
            tipo=PuntoAcceso.Tipo.PORTON,
            alcance=PuntoAcceso.Alcance.COMUN,
            terreno=self.terreno_b,
        )

        # Iniciar sesión como Sofía.

        self.client.force_authenticate(
            user=self.user_a
        )

    # ----------------------------------------------
    # TERRENOS
    # ----------------------------------------------

    def test_list_only_own_terrains(self):

        response = self.client.get(
            "/api/terrenos/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        ids = [
            item["id"]
            for item in response.data
        ]

        self.assertEqual(
            ids,
            [self.terreno_a.id]
        )

    def test_cannot_retrieve_foreign_terrain(self):

        response = self.client.get(
            f"/api/terrenos/{self.terreno_b.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_create_terrain_assigns_current_administrator(self):

        response = self.client.post(
            "/api/terrenos/",
            {
                "nombre": "Nuevo terreno Sofia",
                "direccion": "Nueva direccion",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            response.data["administrador"],
            self.persona_a.id
        )

    def test_cannot_create_terrain_with_foreign_administrator(self):

        response = self.client.post(
            "/api/terrenos/",
            {
                "nombre": "Terreno ajeno",
                "direccion": "Direccion ajena",
                "administrador": self.persona_b.id,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    # ----------------------------------------------
    # VIVIENDAS
    # ----------------------------------------------

    def test_list_only_own_viviendas(self):

        response = self.client.get(
            "/api/viviendas/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        ids = [
            item["id"]
            for item in response.data
        ]

        self.assertEqual(
            ids,
            [self.vivienda_a.id]
        )

    def test_cannot_retrieve_foreign_vivienda(self):

        response = self.client.get(
            f"/api/viviendas/{self.vivienda_b.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_cannot_create_vivienda_in_foreign_terrain(self):

        response = self.client.post(
            "/api/viviendas/",
            {
                "codigo_unidad": "CASA-AJENA",
                "direccion_interna": "Casa ajena",
                "terreno": self.terreno_b.id,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_cannot_change_vivienda_to_foreign_terrain(self):

        response = self.client.patch(
            f"/api/viviendas/{self.vivienda_a.id}/",
            {
                "terreno": self.terreno_b.id,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    # ----------------------------------------------
    # PUNTOS DE ACCESO
    # ----------------------------------------------

    def test_list_only_own_access_points(self):

        response = self.client.get(
            "/api/puntos-acceso/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        ids = [
            item["id"]
            for item in response.data
        ]

        self.assertEqual(
            ids,
            [self.acceso_a.id]
        )

    def test_cannot_retrieve_foreign_access_point(self):

        response = self.client.get(
            f"/api/puntos-acceso/{self.acceso_b.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_cannot_create_access_point_in_foreign_terrain(self):

        response = self.client.post(
            "/api/puntos-acceso/",
            {
                "codigo": "ACC-AJENO",
                "nombre": "Acceso ajeno",
                "tipo": "PORTON",
                "alcance": "COMUN",
                "terreno": self.terreno_b.id,
                "activo": True,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_cannot_change_access_point_to_foreign_terrain(self):

        response = self.client.patch(
            f"/api/puntos-acceso/{self.acceso_a.id}/",
            {
                "terreno": self.terreno_b.id,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_can_create_access_point_in_own_terrain(self):

        response = self.client.post(
            "/api/puntos-acceso/",
            {
                "codigo": "ACC-SOFIA-002",
                "nombre": "Puerta secundaria",
                "tipo": "PUERTA",
                "alcance": "COMUN",
                "terreno": self.terreno_a.id,
                "activo": True,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    # ----------------------------------------------
    # PERSONAS
    # ----------------------------------------------

    def test_persona_list_only_shows_related_people(self):

        response = self.client.get(
            "/api/personas/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        ids = [
            item["id"]
            for item in response.data
        ]

        self.assertIn(
            self.persona_a.id,
            ids
        )

        self.assertIn(
            self.propietario_a.id,
            ids
        )

        self.assertNotIn(
            self.persona_b.id,
            ids
        )

    # ----------------------------------------------
    # USUARIOS SIN PERSONA ACTIVA
    # ----------------------------------------------

    def test_user_without_active_persona_cannot_create_terrain(self):

        user_without_persona = User.objects.create_user(
            username="sin_persona",
            password="TestPassword123!"
        )

        self.client.force_authenticate(
            user=user_without_persona
        )

        response_list = self.client.get(
            "/api/terrenos/"
        )

        self.assertEqual(
            response_list.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response_list.data,
            []
        )

        response_create = self.client.post(
            "/api/terrenos/",
            {
                "nombre": "Terreno no autorizado",
                "direccion": "Direccion de prueba",
            },
            format="json"
        )

        self.assertEqual(
            response_create.status_code,
            status.HTTP_403_FORBIDDEN
        )
