from django.contrib import admin
from .models import (
    Categoria, Producto, Combo, CombosProductos,
    Pedido, UserProfile, CarritoDeCompras, ItemCarrito
)

admin.site.register(Categoria)
admin.site.register(CombosProductos)
admin.site.register(Pedido)
admin.site.register(UserProfile)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'id_categoria', 'valor_unitario', 'stock', 'activo', 'id')
    list_filter = ('activo', 'id_categoria')
    search_fields = ('nombre', 'descripcion')
    list_editable = ('valor_unitario', 'stock', 'activo')
    ordering = ('nombre',)
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'descripcion', 'id_categoria', 'imagen_url'),
        }),
        ('Datos de Inventario y Precio', {
            'fields': ('valor_unitario', 'stock', 'activo'),
        }),
    )


class CombosProductosInline(admin.TabularInline):
    """Permite editar los productos dentro del formulario de Combo"""
    model = Combo.productos.through
    extra = 1


@admin.register(Combo)
class ComboAdmin(admin.ModelAdmin):
    list_display = ('id', 'valor_combo', 'descuento_porcentaje', 'valido_hasta', 'activo')
    search_fields = ('usuario_id__username', 'id')
    list_filter = ('activo', 'valido_hasta')
    inlines = [CombosProductosInline]
    exclude = ('productos',)

class ItemCarritoInline(admin.TabularInline):
    """
    Define cómo se mostrarán los ItemsCarrito dentro de CarritoDeCompras.
    """
    model = ItemCarrito
    fields = ('producto', 'cantidad', 'fecha_agregado')
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
