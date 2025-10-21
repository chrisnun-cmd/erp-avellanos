from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.utils import timezone
from .models import (
    Cliente, MateriaPrima, ProductoTerminado, Proveedor,
    CompraMateriaPrima, InventarioMateriaPrima, InventarioProductoFinal,
    OperacionProcesamiento, CostoMaquila,
    OrdenVenta, ItemOrdenVenta,
    ProveedorServicio, Embarque, ServicioLogistico,
    DocumentacionExportacion, Cotizacion
)

# === Inlines ===
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

# === Clases de Admin (sin @admin.register) ===
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'pais', 'email', 'telefono')

class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'region', 'contacto')

class MateriaPrimaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

class ProductoTerminadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'presentacion', 'precio_kg_usd')
    list_filter = ('tipo',)

class CompraMateriaPrimaAdmin(admin.ModelAdmin):
    list_display = ('proveedor', 'materia_prima', 'cantidad_kg', 'precio_por_kg', 'abastecida')
    list_filter = ('abastecida', 'proveedor')

class InventarioMateriaPrimaAdmin(admin.ModelAdmin):
    list_display = ('materia_prima', 'stock_kg')
    readonly_fields = ('stock_kg',)

class InventarioProductoFinalAdmin(admin.ModelAdmin):
    list_display = ('producto', 'stock_kg')
    readonly_fields = ('stock_kg',)

class OperacionProcesamientoAdmin(admin.ModelAdmin):
    list_display = ('id', 'materia_prima', 'kg_entrada', 'producto_terminado', 'kg_salida_real', 'abastecido_a_inventario')
    inlines = [CostoMaquilaInline]

class OrdenVentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'estado', 'porcentaje_adelanto')
    list_filter = ('estado',)
    inlines = [ItemOrdenVentaInline]

class ProveedorServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'contacto')
    list_filter = ('tipo',)

class EmbarqueAdmin(admin.ModelAdmin):
    list_display = ('orden_venta', 'fecha_embarque')
    inlines = [ServicioLogisticoInline]

class DocumentacionExportacionAdmin(admin.ModelAdmin):
    list_display = ('embarque', 'dus', 'guia_despacho', 'packing_list', 'certificado_origen', 'estado_envio')
    list_filter = ('estado_envio',)

class CotizacionAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'producto', 'cantidad_kg', 'precio_sugerido_kg', 'convertida_a_orden')
    list_filter = ('convertida_a_orden',)

# === Dashboard personalizado ===
class CustomAdminSite(admin.AdminSite):
    site_header = "ERP Sociedad Comercial Los Avellanos Spa"
    site_title = "ERP Avellanos"
    index_title = "Dashboard Operativo"

    def index(self, request, extra_context=None):
        from datetime import timedelta
        hoy = timezone.now().date()
        proximos_7_dias = hoy + timedelta(days=7)

        context = {
            **self.each_context(request),
            'ordenes_pendientes': OrdenVenta.objects.filter(estado='pendiente').count(),
            'operaciones_pendientes': OperacionProcesamiento.objects.filter(abastecido_a_inventario=False).count(),
            'embarques_proximos': Embarque.objects.filter(fecha_embarque__range=[hoy, proximos_7_dias]).count(),
            'docs_pendientes': DocumentacionExportacion.objects.filter(estado_envio='pendiente').count(),
            'inventario_bajo': InventarioProductoFinal.objects.filter(stock_kg__lt=100).count(),
        }
        return render(request, 'admin/dashboard.html', context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [path('', self.index, name='index')]
        return custom_urls + urls

# Reemplazar el admin por defecto
custom_admin_site = CustomAdminSite(name='custom_admin')

# Registrar todos los modelos en el admin personalizado
custom_admin_site.register(Cliente, ClienteAdmin)
custom_admin_site.register(Proveedor, ProveedorAdmin)
custom_admin_site.register(MateriaPrima, MateriaPrimaAdmin)
custom_admin_site.register(ProductoTerminado, ProductoTerminadoAdmin)
custom_admin_site.register(CompraMateriaPrima, CompraMateriaPrimaAdmin)
custom_admin_site.register(InventarioMateriaPrima, InventarioMateriaPrimaAdmin)
custom_admin_site.register(InventarioProductoFinal, InventarioProductoFinalAdmin)
custom_admin_site.register(OperacionProcesamiento, OperacionProcesamientoAdmin)
custom_admin_site.register(OrdenVenta, OrdenVentaAdmin)
custom_admin_site.register(ProveedorServicio, ProveedorServicioAdmin)
custom_admin_site.register(Embarque, EmbarqueAdmin)
custom_admin_site.register(DocumentacionExportacion, DocumentacionExportacionAdmin)
custom_admin_site.register(Cotizacion, CotizacionAdmin)