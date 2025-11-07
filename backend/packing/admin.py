from django.contrib import admin
from .models import Productor, Variedad, TipoEnvase, Pallet, Distribuidor, TipoPocillo, Linea,  GrupoTerminado


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
    list_display = ('codigo', 'productor', 'variedad', 'tipo_envase', 'cantidad_cajas', 'peso_neto', 'fecha_creacion')
    search_fields = ('codigo',)
    list_filter = ('productor', 'variedad', 'tipo_envase')

@admin.register(Distribuidor)
class DistribuidorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)
    verbose_name = "Distribuidor"
    verbose_name_plural = "Distribuidores"


@admin.register(TipoPocillo)
class TipoPocilloAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)
    verbose_name = "Tipo de Pocillo"
    verbose_name_plural = "Tipos de Pocillo"


@admin.register(Linea)
class LineaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)
    verbose_name = "Línea"
    verbose_name_plural = "Líneas"


@admin.register(GrupoTerminado)
class GrupoTerminadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'grupo_proceso', 'distribuidor', 'tipo_pocillo', 'linea', 'cantidad_cajas', 'fecha')
    search_fields = ('grupo_proceso__id_grupo', 'distribuidor__nombre')
    list_filter = ('distribuidor', 'tipo_pocillo', 'linea')