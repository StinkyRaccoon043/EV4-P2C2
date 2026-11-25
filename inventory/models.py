from django.db import models

class Equipment(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    is_available = models.BooleanField(default=True)


class Persona(models.Model):
    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.rut})"


class Vivienda(models.Model):
    codigo_unidad = models.CharField(max_length=20, unique=True)
    direccion_interna = models.CharField(max_length=150)
    propietarios = models.ManyToManyField(
        Persona,
        related_name="viviendas",
        blank=True,
    )

    def __str__(self):
        return self.codigo_unidad