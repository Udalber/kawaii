from django.shortcuts import render
from .models import Producto


def lista_productos(request):
    """
    Vista que recupera todos los productos y los pasa a la plantilla.
    """
    # 1. Recuperar datos: Obtiene todos los objetos Producto de la base de datos
    productos = Producto.objects.all().filter(activo=True).order_by('nombre')

    # 2. Definir el contexto: Es el diccionario que enviará los datos a la plantilla
    contexto = {
        'productos': productos,
        'titulo': 'Nuestra Colección de Productos'
    }

    # 3. Renderizar: Retorna una respuesta HTML usando la plantilla 'productos/lista.html'
    return render(request, 'productos/lista.html', contexto)
