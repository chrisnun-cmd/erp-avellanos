from django.db import models

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    pais = models.CharField(max_length=50)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    def __str__(self):
        return self.nombre

class MateriaPrima(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.nombre

class ProductoTerminado(models.Model):
    TIPO_CHOICES = [
        ('fresco', 'Fresco'),
        ('congelado', 'Congelado'),
        ('conserva', 'En conserva'),
    ]
    nombre = models.CharField(max_length=100, default="Mejillón")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    presentacion = models.CharField(max_length=100)
    precio_kg_usd = models.DecimalField(max_digits=8, decimal_places=2)
    def __str__(self):
        return f"{self.nombre} - {self.tipo} ({self.presentacion})"

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    region = models.CharField(max_length=50, blank=True)
    contacto = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    def __str__(self):
        return self.nombre

class CompraMateriaPrima(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    materia_prima = models.ForeignKey(MateriaPrima, on_delete=models.CASCADE)
    cantidad_kg = models.DecimalField(max_digits=12, decimal_places=3)
    precio_por_kg = models.DecimalField(max_digits=12, decimal_places=2)
    moneda = models.CharField(max_length=3, choices=[('USD', 'USD'), ('CLP', 'CLP')], default='USD')
    fecha = models.DateField(auto_now_add=True)
    abastecida = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.cantidad_kg} kg de {self.materia_prima} de {self.proveedor}"

class InventarioMateriaPrima(models.Model):
    materia_prima = models.OneToOneField(MateriaPrima, on_delete=models.CASCADE)
    stock_kg = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    def __str__(self):
        return f"{self.stock_kg} kg de {self.materia_prima}"

class InventarioProductoFinal(models.Model):
    producto = models.OneToOneField(ProductoTerminado, on_delete=models.CASCADE)
    stock_kg = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    def __str__(self):
        return f"{self.stock_kg} kg de {self.producto}"

class OperacionProcesamiento(models.Model):
    materia_prima = models.ForeignKey(MateriaPrima, on_delete=models.PROTECT)
    kg_entrada = models.DecimalField(max_digits=12, decimal_places=3)
    producto_terminado = models.ForeignKey(ProductoTerminado, on_delete=models.PROTECT)
    rendimiento_esperado_pct = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    kg_salida_real = models.DecimalField(max_digits=12, decimal_places=3)
    fecha = models.DateField(auto_now_add=True)
    abastecido_a_inventario = models.BooleanField(default=False)
    def __str__(self):
        return f"OP-{self.id}: {self.kg_entrada} kg → {self.kg_salida_real} kg"

class CostoMaquila(models.Model):
    operacion = models.ForeignKey(OperacionProcesamiento, on_delete=models.CASCADE, related_name='costos')
    concepto = models.CharField(max_length=200)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    moneda = models.CharField(max_length=3, choices=[('USD', 'USD'), ('CLP', 'CLP')], default='USD')
    fecha = models.DateField()
    def __str__(self):
        return f"{self.concepto}: {self.monto} {self.moneda}"

class OrdenVenta(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    porcentaje_adelanto = models.DecimalField(max_digits=5, decimal_places=2)
    condicion_saldo = models.CharField(
        max_length=50,
        choices=[
            ('contra_copia', 'Contra copia de documentos'),
            ('contra_originales', 'Contra recepción de documentos originales'),
        ]
    )
    fecha_estimada_pago_saldo = models.DateField()
    fecha = models.DateField(auto_now_add=True)
    def __str__(self):
        return f"OV-{self.id} - {self.cliente}"

class ItemOrdenVenta(models.Model):
    orden = models.ForeignKey(OrdenVenta, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(ProductoTerminado, on_delete=models.PROTECT)
    cantidad_kg = models.DecimalField(max_digits=12, decimal_places=3)
    precio_por_kg = models.DecimalField(max_digits=12, decimal_places=2)
    @property
    def cantidad_lb(self):
        return float(self.cantidad_kg) * 2.20462
    @property
    def subtotal_usd(self):
        return float(self.cantidad_kg) * float(self.precio_por_kg)
    def __str__(self):
        return f"{self.cantidad_kg} kg de {self.producto}"

class ProveedorServicio(models.Model):
    TIPO_CHOICES = [
        ('naviera', 'Naviera'),
        ('forwarder', 'Forwarder'),
        ('aduana', 'Agente de aduana'),
        ('flete', 'Flete terrestre'),
        ('broker', 'Broker'),
        ('otro', 'Otro'),
    ]
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    contacto = models.CharField(max_length=100, blank=True)
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"

class Embarque(models.Model):
    orden_venta = models.ForeignKey(OrdenVenta, on_delete=models.CASCADE)
    fecha_embarque = models.DateField()
    def __str__(self):
        return f"Embarque OV-{self.orden_venta.id}"

class ServicioLogistico(models.Model):
    ESTADO_PAGO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('pagada', 'Pagada'),
    ]
    embarque = models.ForeignKey(Embarque, on_delete=models.CASCADE, related_name='servicios')
    proveedor = models.ForeignKey(ProveedorServicio, on_delete=models.PROTECT)
    documento_referencia = models.CharField(max_length=100)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    moneda = models.CharField(max_length=3, choices=[('USD', 'USD'), ('CLP', 'CLP')], default='USD')
    fecha_vencimiento = models.DateField()
    estado_pago = models.CharField(max_length=20, choices=ESTADO_PAGO_CHOICES, default='pendiente')
    def __str__(self):
        return f"{self.proveedor}: {self.monto} {self.moneda}"

class DocumentacionExportacion(models.Model):
    ESTADO_ENVIO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('enviada', 'Enviada'),
    ]
    embarque = models.OneToOneField(Embarque, on_delete=models.CASCADE)
    dus = models.BooleanField(default=False)
    guia_despacho = models.BooleanField(default=False)
    packing_list = models.BooleanField(default=False)
    certificado_origen = models.BooleanField(default=False)
    otros_certificados = models.TextField(blank=True)
    fecha_arribo_estimada = models.DateField()
    plazo_envio_courier = models.DateField()
    estado_envio = models.CharField(max_length=20, choices=ESTADO_ENVIO_CHOICES, default='pendiente')
    def __str__(self):
        return f"Doc OV-{self.embarque.orden_venta.id}"

class Cotizacion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    producto = models.ForeignKey(ProductoTerminado, on_delete=models.PROTECT)
    cantidad_kg = models.DecimalField(max_digits=12, decimal_places=3)
    costo_estimado_total = models.DecimalField(max_digits=12, decimal_places=2)
    margen_pct = models.DecimalField(max_digits=5, decimal_places=2)
    precio_sugerido_kg = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fecha = models.DateField(auto_now_add=True)
    convertida_a_orden = models.BooleanField(default=False)
    def __str__(self):
        return f"Cotización {self.id} - {self.cliente}"