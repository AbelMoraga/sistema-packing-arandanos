from django.contrib import admin
from .models import (
    Productor, Variedad, TipoEnvase, Pallet,
    Distribuidor, TipoPocillo, Linea,
    PalletTerminado, IQFDescarte, GrupoProceso
)

@admin.register(Productor)
class ProductorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)

@admin.register(Variedad)
class VariedadAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)

@admin.register(TipoEnvase)
class TipoEnvaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)

@admin.register(Pallet)
class PalletAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'productor', 'variedad', 'tipo_envase', 'cantidad_cajas', 'peso_neto', 'bloqueado_recepcion', 'bloqueado_proceso')
    list_filter = ('productor', 'variedad', 'tipo_envase')
    search_fields = ('codigo',)

@admin.register(Distribuidor)
class DistribuidorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)

@admin.register(TipoPocillo)
class TipoPocilloAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)

@admin.register(Linea)
class LineaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)

@admin.register(PalletTerminado)
class PalletTerminadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'distribuidor', 'tipo_pocillo', 'linea', 'cantidad_cajas', 'calidad', 'fecha')
    list_filter = ('calidad', 'linea', 'distribuidor')
    search_fields = ('distribuidor__nombre',)

@admin.register(IQFDescarte)
class IQFDescarteAdmin(admin.ModelAdmin):
    list_display = ('id', 'grupo_proceso', 'peso_iqf', 'peso_descarte', 'fecha_registro')
    search_fields = ('grupo_proceso__id_grupo',)

@admin.register(GrupoProceso)
class GrupoProcesoAdmin(admin.ModelAdmin):
    list_display = ('id_grupo', 'productor', 'variedad', 'fecha_creacion')
    search_fields = ('id_grupo', 'productor__nombre')
