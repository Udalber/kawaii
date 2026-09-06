from django.contrib import admin
from .models import (
    Categoria, Producto, Combo, CombosProductos,
    Pedido, DetallePedido, UserProfile, CarritoDeCompras, ItemCarrito
)

admin.site.register(Categoria)
admin.site.register(CombosProductos)
admin.site.register(UserProfile)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'id_categoria', 'valor_unitario', 'descuento_porcentaje', 'stock', 'activo', 'id')
    list_filter = ('activo', 'id_categoria')
    search_fields = ('nombre', 'descripcion')
    list_editable = ('valor_unitario', 'descuento_porcentaje', 'stock', 'activo')
    ordering = ('nombre',)
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'descripcion', 'id_categoria', 'imagen', 'imagen_url'),
            'description': 'Puedes subir una imagen desde tu computador o indicar un enlace URL.'
        }),
        ('Datos de Inventario, Precio y Descuento', {
            'fields': ('valor_unitario', 'descuento_porcentaje', 'stock', 'activo'),
        }),
    )


class CombosProductosInline(admin.TabularInline):
    """Permite editar los productos dentro del formulario de Combo"""
    model = Combo.productos.through
    extra = 0


@admin.register(Combo)
class ComboAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'valor_combo', 'descuento_porcentaje', 'valido_hasta', 'activo')
    search_fields = ('nombre', 'descripcion', 'usuario_id__username')
    list_filter = ('activo', 'valido_hasta')
    list_editable = ('valor_combo', 'descuento_porcentaje', 'activo')
    ordering = ('nombre',)
    inlines = [CombosProductosInline]
    exclude = ('productos',)
    fieldsets = (
        ('Información del combo', {
            'fields': ('nombre', 'descripcion', 'imagen', 'imagen_url', 'activo'),
            'description': 'Puedes subir una imagen desde tu computador o indicar un enlace URL.'
        }),
        ('Precio y vigencia', {
            'fields': ('valor_combo', 'descuento_porcentaje', 'valido_hasta'),
        }),
        ('Información adicional', {
            'fields': ('usuario_id', 'numero_productos'),
        }),
    )


class DetallePedidoInline(admin.TabularInline):
    """Muestra los productos y combos incluidos en el pedido."""
    model = DetallePedido
    extra = 0
    readonly_fields = ('producto', 'combo', 'cantidad', 'precio_item')


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id_corto', 'id_usuario', 'fecha_pedido', 'valor_pagado', 'estado', 'empresa_envio', 'numero_guia', 'tiene_comprobante')
    list_editable = ('estado', 'empresa_envio', 'numero_guia')
    list_filter = ('estado', 'fecha_pedido')
    search_fields = ('id', 'id_usuario__username', 'id_usuario__email', 'numero_guia', 'empresa_envio')
    ordering = ('-fecha_pedido',)
    inlines = [DetallePedidoInline]
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('id_usuario', 'estado', 'valor_pagado', 'metodo_pago', 'detalle_pago'),
        }),
        ('Comprobante de Pago', {
            'fields': ('comprobante_pago',),
            'description': 'Sube la imagen o foto del comprobante de transferencia / pago de la orden.'
        }),
        ('Información de Envío y Guía', {
            'fields': ('empresa_envio', 'numero_guia'),
            'description': 'Completa estos campos cuando el pedido esté enviado para que el cliente pueda ver su guía en "Mis Pedidos".'
        }),
    )

    def id_corto(self, obj):
        return obj.codigo_pedido
    id_corto.short_description = "N° Pedido"

    def tiene_comprobante(self, obj):
        return bool(obj.comprobante_pago)
    tiene_comprobante.boolean = True
    tiene_comprobante.short_description = "Comprobante"


class ItemCarritoInline(admin.TabularInline):
    """
    Define cómo se mostrarán los ItemsCarrito dentro de CarritoDeCompras.
    """
    model = ItemCarrito
    fields = ('producto', 'combo', 'cantidad', 'fecha_agregado')
    readonly_fields = ('fecha_agregado',)
    extra = 1


@admin.register(CarritoDeCompras)
class CarritoDeComprasAdmin(admin.ModelAdmin):
    """
    Configuración para mostrar la información del Carrito.
    """
    list_display = ('usuario', 'fecha_creacion', 'contar_productos')
    search_fields = ('usuario__username', 'usuario__first_name')
    inlines = [ItemCarritoInline]
    def contar_productos(self, obj):
        return obj.items.count()
    contar_productos.short_description = "N° de Productos"
