from django.db import models
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

#
# ENTIDADES BASE

class Productor(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.nombre


class Variedad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.nombre


class TipoEnvase(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.nombre


class Distribuidor(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.nombre


class TipoPocillo(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.nombre


class Linea(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.nombre



# PROCESOS INTERNOS

class GrupoProceso(models.Model):
    id_grupo = models.AutoField(primary_key=True)
    productor = models.ForeignKey(Productor, on_delete=models.CASCADE)
    variedad = models.ForeignKey(Variedad, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Grupo {self.id_grupo} - {self.productor} ({self.variedad})"


class Pallet(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.PositiveIntegerField(unique=True, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    productor = models.ForeignKey(Productor, on_delete=models.CASCADE)
    variedad = models.ForeignKey(Variedad, on_delete=models.CASCADE)
    tipo_envase = models.ForeignKey(TipoEnvase, on_delete=models.CASCADE)
    grupo = models.ForeignKey(GrupoProceso, on_delete=models.SET_NULL, null=True, blank=True)

    cantidad_cajas = models.PositiveIntegerField(default=0)
    peso_neto = models.DecimalField(max_digits=6, decimal_places=1, default=0.0)

  
    enfriado = models.BooleanField(default=False)
    fumigado = models.BooleanField(default=False)
    pre_procesos = models.BooleanField(default=False)
    organico = models.BooleanField(default=False)
    procesado = models.BooleanField(default=False)

  
    bloqueado_recepcion = models.BooleanField(default=False)
    bloqueado_proceso = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.codigo is None:
            ultimo = Pallet.objects.all().order_by('-codigo').first()
            self.codigo = ultimo.codigo + 1 if ultimo else 1000
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pallet {self.codigo} - {self.variedad}"



# PROCESOS TERMINADOS

CALIDAD_CHOICES = [
    ('Rechazado', 'Rechazado'),
    ('Baja', 'Baja'),
    ('Buena', 'Buena'),
    ('Excelente', 'Excelente'),
]

class PalletTerminado(models.Model):
    distribuidor = models.ForeignKey(Distribuidor, on_delete=models.CASCADE)
    tipo_pocillo = models.ForeignKey(TipoPocillo, on_delete=models.CASCADE)
    linea = models.ForeignKey(Linea, on_delete=models.CASCADE)
    variedad = models.ForeignKey(Variedad, on_delete=models.CASCADE, null=True, blank=True)
    cantidad_cajas = models.PositiveIntegerField()
    calidad = models.CharField(max_length=20, choices=[
        ('Rechazado', 'Rechazado'),
        ('Baja', 'Baja'),
        ('Buena', 'Buena'),
        ('Excelente', 'Excelente'),
    ])
    estado = models.CharField(max_length=20, choices=[
        ('Por enviar', 'Por enviar'),
        ('Enviado', 'Enviado'),
    ], default='Por enviar') 
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.distribuidor} - {self.calidad} ({self.estado})"


# IQF Y DESCARTE


    
class IQFDescarte(models.Model):
    grupo_proceso = models.OneToOneField(GrupoProceso, on_delete=models.CASCADE)

    peso_iqf = models.FloatField()
    peso_descarte = models.FloatField()

    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    fecha_retiro = models.DateTimeField(null=True, blank=True)

    estado = models.CharField(
        max_length=20,
        choices=[
            ("EN_IQF", "En IQF"),
            ("RETIRADO", "Retirado"),
            ("DESPACHADO", "Despachado"),
        ],
        default="EN_IQF"
    )

    productor = models.CharField(max_length=100)
    variedad = models.CharField(max_length=100)

    peso_final = models.FloatField(null=True, blank=True)

    def dias_en_iqf(self):
        from django.utils import timezone

        # Si NO tiene fecha de ingreso → imposible calcular
        if not self.fecha_ingreso:
            return "-"

        # Si sigue en IQF → usar fecha actual
        if self.estado == "EN_IQF":
            return (timezone.now() - self.fecha_ingreso).days

        # Si no tiene fecha de retiro (error de datos)
        if not self.fecha_retiro:
            return "-"

        # Si tiene ambas fechas
        return (self.fecha_retiro - self.fecha_ingreso).days

    # admin
    @property
    def fecha_registro(self):
        return self.fecha_ingreso

    def __str__(self):
        return f"IQF {self.id} - Grupo {self.grupo_proceso.id_grupo}"


# models.py


class RegistroActividad(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    accion = models.CharField(max_length=255)
    modulo = models.CharField(max_length=100)
    detalle = models.TextField(blank=True)
    fecha = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.usuario} - {self.accion} - {self.fecha}"