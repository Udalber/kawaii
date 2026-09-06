from django.db import migrations


def crear_scoop_normal(apps, schema_editor):
    Categoria = apps.get_model('sorpresas_kawai', 'Categoria')
    Producto = apps.get_model('sorpresas_kawai', 'Producto')

    categoria, _ = Categoria.objects.get_or_create(nombre='Sorpresa')
    Producto.objects.get_or_create(
        nombre='Scoop Normal',
        id_categoria=categoria,
        defaults={
            'descripcion': 'Una cucharada sorpresa con artículos kawaii seleccionados al azar.',
            'valor_unitario': 30000,
            'stock': 100,
            'activo': True,
        },
    )


def eliminar_scoop_normal(apps, schema_editor):
    Producto = apps.get_model('sorpresas_kawai', 'Producto')
    Categoria = apps.get_model('sorpresas_kawai', 'Categoria')
    Producto.objects.filter(nombre='Scoop Normal').delete()
    Categoria.objects.filter(nombre='Sorpresa').delete()


class Migration(migrations.Migration):
    dependencies = [('sorpresas_kawai', '0005_combo_nombre')]

    operations = [migrations.RunPython(crear_scoop_normal, eliminar_scoop_normal)]
