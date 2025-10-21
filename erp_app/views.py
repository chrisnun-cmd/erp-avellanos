from django.shortcuts import render
from django.utils import timezone
from .models import (
    OrdenVenta, OperacionProcesamiento, Embarque,
    DocumentacionExportacion, InventarioProductoFinal
)

def dashboard_view(request):
    ordenes_pendientes = OrdenVenta.objects.filter(estado='pendiente').count()
    operaciones_pendientes = OperacionProcesamiento.objects.filter(abastecido_a_inventario=False).count()
    embarques_proximos = Embarque.objects.filter(
        fecha_embarque__gte=timezone.now().date()
    ).count()
    docs_pendientes = DocumentacionExportacion.objects.filter(estado_envio='pendiente').count()
    inventario_bajo = InventarioProductoFinal.objects.filter(stock_kg__lt=100).count()

    context = {
        'ordenes_pendientes': ordenes_pendientes,
        'operaciones_pendientes': operaciones_pendientes,
        'embarques_proximos': embarques_proximos,
        'docs_pendientes': docs_pendientes,
        'inventario_bajo': inventario_bajo,
    }
    return render(request, 'dashboard.html', context)