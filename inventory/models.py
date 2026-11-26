
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone


class Equipment(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Persona(models.Model):
    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    activo = models.BooleanField(default=True)

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="persona"
    )

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.rut})"


class Terreno(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)

    administrador = models.ForeignKey(
        Persona,
        on_delete=models.PROTECT,
        related_name="terrenos_administrados"
    )

    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Vivienda(models.Model):
    codigo_unidad = models.CharField(max_length=20, unique=True)
    direccion_interna = models.CharField(max_length=150)

    terreno = models.ForeignKey(
        Terreno,
        on_delete=models.PROTECT,
        related_name="viviendas",
        null=True,
        blank=True
    )

    propietarios = models.ManyToManyField(
        Persona,
        related_name="viviendas",
        blank=True,
    )

    def __str__(self):
        return self.codigo_unidad


class PuntoAcceso(models.Model):

    class Tipo(models.TextChoices):
        PORTON = "PORTON", "Portón"
        PUERTA = "PUERTA", "Puerta"
        BARRERA = "BARRERA", "Barrera"
        TORNIQUETE = "TORNIQUETE", "Torniquete"

    class Alcance(models.TextChoices):
        COMUN = "COMUN", "Acceso común"
        PRIVADO = "PRIVADO", "Acceso privado"

    codigo = models.CharField(max_length=30)
    nombre = models.CharField(max_length=100)

    tipo = models.CharField(
        max_length=20,
        choices=Tipo.choices,
        default=Tipo.PORTON
    )

    alcance = models.CharField(
        max_length=20,
        choices=Alcance.choices,
        default=Alcance.COMUN
    )

    terreno = models.ForeignKey(
        Terreno,
        on_delete=models.PROTECT,
        related_name="puntos_acceso"
    )

    vivienda = models.ForeignKey(
        Vivienda,
        on_delete=models.PROTECT,
        related_name="puntos_acceso",
        null=True,
        blank=True
    )

    activo = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["terreno", "codigo"],
                name="uniq_codigo_punto_acceso_terreno"
            )
        ]

    def clean(self):
        if self.alcance == self.Alcance.COMUN and self.vivienda_id:
            raise ValidationError({
                "vivienda": "Un acceso común no debe asociarse a una vivienda."
            })

        if self.alcance == self.Alcance.PRIVADO and not self.vivienda_id:
            raise ValidationError({
                "vivienda": "Un acceso privado debe pertenecer a una vivienda."
            })

        if self.vivienda_id and self.vivienda.terreno_id != self.terreno_id:
            raise ValidationError({
                "vivienda": "La vivienda debe pertenecer al mismo terreno."
            })

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class ParticipacionVivienda(models.Model):

    class Rol(models.TextChoices):
        PROPIETARIO_ADMINISTRADOR = (
            "PROPIETARIO_ADMINISTRADOR",
            "Propietario administrador"
        )
        PROPIETARIO = "PROPIETARIO", "Propietario"
        ARRENDATARIO = "ARRENDATARIO", "Arrendatario"
        CONVIVIENTE = "CONVIVIENTE", "Conviviente"

    persona = models.ForeignKey(
        Persona,
        on_delete=models.PROTECT,
        related_name="participaciones"
    )

    vivienda = models.ForeignKey(
        Vivienda,
        on_delete=models.PROTECT,
        related_name="participaciones"
    )

    rol = models.CharField(
        max_length=30,
        choices=Rol.choices
    )

    activa = models.BooleanField(default=True)

    fecha_inicio = models.DateField(
        default=timezone.localdate
    )

    fecha_fin = models.DateField(
        null=True,
        blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["persona", "vivienda"],
                condition=Q(activa=True),
                name="uniq_participacion_activa"
            ),
            models.UniqueConstraint(
                fields=["vivienda"],
                condition=Q(
                    activa=True,
                    rol="PROPIETARIO_ADMINISTRADOR"
                ),
                name="uniq_admin_vivienda_activo"
            )
        ]

    def __str__(self):
        return (
            f"{self.persona} - {self.vivienda} "
            f"({self.get_rol_display()})"
        )
