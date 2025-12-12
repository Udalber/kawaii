# ecommerce/admin.py

from django.contrib import admin
from .models import (
    Categoria, Producto, Combo, CombosProductos,
    Pedido, UserProfile
)

# 1. Registro básico de modelos
admin.site.register(Categoria)
# admin.site.register(Producto) # Lo registraremos con un Admin personalizado
admin.site.register(CombosProductos)
admin.site.register(Pedido)
admin.site.register(UserProfile)


# 2. Clase de configuración para mejorar la vista de Producto
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    # Campos que se muestran en la lista de Productos
    list_display = ('nombre', 'id_categoria', 'valor_unitario', 'stock', 'activo', 'id')

    # Filtros laterales
    list_filter = ('activo', 'id_categoria')

    # Campos que se pueden buscar
    search_fields = ('nombre', 'descripcion')

    # Campos que se pueden editar directamente desde la lista (cuidado con abusar)
    list_editable = ('valor_unitario', 'stock', 'activo')

    # Ordenar por defecto
    ordering = ('nombre',)

    # Separación y organización de campos en la página de edición
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'descripcion', 'id_categoria', 'imagen_url'),
        }),
        ('Datos de Inventario y Precio', {
            'fields': ('valor_unitario', 'stock', 'activo'),
        }),
    )


# 3. Clase de configuración para Combo (para ver los productos en el combo)
class CombosProductosInline(admin.TabularInline):
    """Permite editar los productos dentro del formulario de Combo"""
    model = Combo.productos.through  # Usa la tabla intermedia CombosProductos
    extra = 1  # Número de formularios vacíos para añadir nuevos productos


@admin.register(Combo)
class ComboAdmin(admin.ModelAdmin):
    list_display = ('id', 'valor_combo', 'descuento_porcentaje', 'valido_hasta', 'activo')
    search_fields = ('usuario_id__username', 'id')  # Búsqueda por el usuario creador
    list_filter = ('activo', 'valido_hasta')

    # Incluir el in-line para gestionar los productos dentro del combo
    inlines = [CombosProductosInline]

    # Excluye el campo 'productos' porque ya se maneja en el inline
    exclude = ('productos',)