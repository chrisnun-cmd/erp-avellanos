from django.contrib import admin
from .models import (
    Cliente, MateriaPrima, ProductoTerminado, Proveedor,
    CompraMateriaPrima, InventarioMateriaPrima, InventarioProductoFinal,
    OperacionProcesamiento, CostoMaquila,
    OrdenVenta, ItemOrdenVenta,
    ProveedorServicio, Embarque, ServicioLogistico,
    DocumentacionExportacion, Cotizacion
)

admin.site.site_header = "ERP Sociedad Comercial Los Avellanos Spa"
admin.site.site_title = "ERP Avellanos"
admin.site.index_title = "Panel de Administración"

class CostoMaquilaInline(admin.TabularInline):
    model = CostoMaquila
    extra = 1

class ItemOrdenVentaInline(admin.TabularInline):
    model = ItemOrdenVenta
    extra = 1
    readonly_fields = ('cantidad_lb', 'subtotal_usd')

class ServicioLogisticoInline(admin.TabularInline):
    model = ServicioLogistico
    extra = 1

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'pais', 'email', 'telefono')

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'region', 'contacto')

@admin.register(MateriaPrima)
class MateriaPrimaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

@admin.register(ProductoTerminado)
class ProductoTerminadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'presentacion', 'precio_kg_usd')
    list_filter = ('tipo',)

@admin.register(CompraMateriaPrima)
class CompraMateriaPrimaAdmin(admin.ModelAdmin):
    list_display = ('proveedor', 'materia_prima', 'cantidad_kg', 'precio_por_kg', 'abastecida')
    list_filter = ('abastecida', 'proveedor')

@admin.register(InventarioMateriaPrima)
class InventarioMateriaPrimaAdmin(admin.ModelAdmin):
    list_display = ('materia_prima', 'stock_kg')
    readonly_fields = ('stock_kg',)

@admin.register(InventarioProductoFinal)
class InventarioProductoFinalAdmin(admin.ModelAdmin):
    list_display = ('producto', 'stock_kg')
    readonly_fields = ('stock_kg',)

@admin.register(OperacionProcesamiento)
class OperacionProcesamientoAdmin(admin.ModelAdmin):
    list_display = ('id', 'materia_prima', 'kg_entrada', 'producto_terminado', 'kg_salida_real', 'abastecido_a_inventario')
    inlines = [CostoMaquilaInline]

@admin.register(OrdenVenta)
class OrdenVentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'estado', 'porcentaje_adelanto')
    list_filter = ('estado',)
    inlines = [ItemOrdenVentaInline]

@admin.register(ProveedorServicio)
class ProveedorServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'contacto')
    list_filter = ('tipo',)

@admin.register(Embarque)
class EmbarqueAdmin(admin.ModelAdmin):
    list_display = ('orden_venta', 'fecha_embarque')
    inlines = [ServicioLogisticoInline]

@admin.register(DocumentacionExportacion)
class DocumentacionExportacionAdmin(admin.ModelAdmin):
    list_display = ('embarque', 'dus', 'guia_despacho', 'packing_list', 'certificado_origen', 'estado_envio')
    list_filter = ('estado_envio',)

@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'producto', 'cantidad_kg', 'precio_sugerido_kg', 'convertida_a_orden')
    list_filter = ('convertida_a_orden',)