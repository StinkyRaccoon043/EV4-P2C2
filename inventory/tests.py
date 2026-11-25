from django.test import TestCase
from rest_framework.test import APITestCase


class PersonaApiTests(APITestCase):
    def test_create_person_and_reject_duplicate_rut(self):
        person = {
            "rut": "12345678-9",
            "nombre": "Ana",
            "apellido": "Perez",
            "email": "ana@example.com",
        }

        response = self.client.post("/api/personas/", person, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["rut"], person["rut"])

        duplicate = dict(person, email="otra@example.com")
        response = self.client.post("/api/personas/", duplicate, format="json")

        self.assertEqual(response.status_code, 400)


class ViviendaApiTests(APITestCase):
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
        owner_ids = [first_person.data["id"], second_person.data["id"]]

        created = self.client.post(
            "/api/viviendas/",
            {
                "codigo_unidad": "Depto 402",
                "direccion_interna": "Torre Norte, Piso 4",
                "propietarios": owner_ids,
            },
            format="json",
        )

        self.assertEqual(created.status_code, 201)
        self.assertCountEqual(created.data["propietarios"], owner_ids)

        updated = self.client.put(
            f"/api/viviendas/{created.data['id']}/",
            {
                "codigo_unidad": "Depto 402",
                "direccion_interna": "Torre Norte, Piso 5",
                "propietarios": [owner_ids[0]],
            },
            format="json",
        )

        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.data["direccion_interna"], "Torre Norte, Piso 5")
        self.assertEqual(updated.data["propietarios"], [owner_ids[0]])
