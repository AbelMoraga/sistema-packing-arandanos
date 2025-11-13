from django.db import models

# -----------------------
# ENTIDADES BASE
# -----------------------
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


# -----------------------
# PROCESOS INTERNOS
# -----------------------
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

    # Estados
    enfriado = models.BooleanField(default=False)
    fumigado = models.BooleanField(default=False)
    pre_procesos = models.BooleanField(default=False)
    organico = models.BooleanField(default=False)
    procesado = models.BooleanField(default=False)

    # Bloqueos
    bloqueado_recepcion = models.BooleanField(default=False)
    bloqueado_proceso = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.codigo is None:
            ultimo = Pallet.objects.all().order_by('-codigo').first()
            self.codigo = ultimo.codigo + 1 if ultimo else 1000
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pallet {self.codigo} - {self.variedad}"


# -----------------------
# PROCESOS TERMINADOS
# -----------------------
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
    ], default='Por enviar')  # 👈 aquí se establece el estado inicial
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.distribuidor} - {self.calidad} ({self.estado})"

# -----------------------
# IQF Y DESCARTE
# -----------------------
class IQFDescarte(models.Model):
    grupo_proceso = models.OneToOneField(GrupoProceso, on_delete=models.CASCADE)
    peso_iqf = models.DecimalField(max_digits=6, decimal_places=1)
    peso_descarte = models.DecimalField(max_digits=6, decimal_places=1)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"IQF y Descarte - Grupo {self.grupo_proceso.id_grupo}"
