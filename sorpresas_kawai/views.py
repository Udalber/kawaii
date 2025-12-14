from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.db import transaction, IntegrityError
from django.db.models import Count
from .models import Producto, Categoria, CarritoDeCompras, ItemCarrito, Pedido, DetallePedido
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Producto
from django.contrib.auth import logout
from django.shortcuts import redirect



def logout_view(request):
    logout(request)
    return redirect('/login/')


def login_view(request):
    error = None

    if request.method == "POST":
        username = request.POST.get("username")  # corregido para coincidir con el input
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Redirigir según tipo de usuario
            if user.is_staff:
                return redirect('/admin/')
            else:
                return redirect('inicio')
        else:
            error = 'Usuario o contraseña incorrectos.'

    return render(request, 'admin/logintest.html', {'error': error})


@login_required
def lista_productos(request):
    categoria_slug = request.GET.get('categoria')
    productos_query = Producto.objects.filter(activo=True).order_by("nombre")
    if categoria_slug:
        productos_query = productos_query.filter(id_categoria__nombre__iexact=categoria_slug)
    productos = productos_query.all()
    categorias = Categoria.objects.filter(
        productos__activo=True
    ).annotate(num_productos=Count('productos')).order_by(
        'nombre')

    productos_en_carrito = {}

    try:
        carrito = CarritoDeCompras.objects.get(usuario=request.user)
        items = ItemCarrito.objects.filter(carrito=carrito)

        for item in items:
            productos_en_carrito[item.producto.id] = item.cantidad

    except CarritoDeCompras.DoesNotExist:
        pass

    contexto = {
        "productos": productos,
        "categorias": categorias,
        "categoria_seleccionada": categoria_slug,
        "titulo": "Nuestra Colección de Productos",
        "productos_en_carrito": productos_en_carrito,
    }

    return render(request, "productos/lista.html", contexto)


@login_required
def agregar_a_carrito(request, producto_id):
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id=producto_id)
        carrito, creado = CarritoDeCompras.objects.get_or_create(usuario=request.user)
        item_carrito, item_creado = ItemCarrito.objects.get_or_create(
            carrito=carrito,
            producto=producto,
            defaults={'cantidad': 1}
        )
        if not item_creado:
            item_carrito.cantidad += 1
            item_carrito.save()

        return redirect(request.META.get('HTTP_REFERER', 'lista_productos'))

    return redirect('lista_productos')


@login_required
def quitar_de_carrito(request, producto_id):
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id=producto_id)
        try:
            carrito = CarritoDeCompras.objects.get(usuario=request.user)
            item_carrito = ItemCarrito.objects.get(carrito=carrito, producto=producto)
            if item_carrito.cantidad > 1:
                item_carrito.cantidad -= 1
                item_carrito.save()
            elif item_carrito.cantidad == 1:
                item_carrito.delete()

        except CarritoDeCompras.DoesNotExist:
            pass
        except ItemCarrito.DoesNotExist:
            pass

        return redirect(request.META.get('HTTP_REFERER', 'lista_productos'))

    return redirect('lista_productos')


@login_required
def ver_carrito(request):
    carrito = None
    items_carrito = []
    subtotal = 0
    total = 0
    costo_envio = 5000

    try:
        carrito = CarritoDeCompras.objects.get(usuario=request.user)
        items_carrito = ItemCarrito.objects.filter(carrito=carrito).select_related('producto')
        for item in items_carrito:
            item.precio_total = item.cantidad * item.producto.valor_unitario
            subtotal += item.precio_total

    except CarritoDeCompras.DoesNotExist:
        pass

    if subtotal > 0:
        total = subtotal + costo_envio

    contexto = {
        'carrito': carrito,
        'items': items_carrito,
        'subtotal': subtotal,
        'costo_envio': costo_envio,
        'total': total,
    }

    return render(request, 'carrito/detalle.html', contexto)

 
def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, 'admin/register.html')

        if User.objects.filter(username=email).exists():
            messages.error(request, "El usuario ya existe.")
            return render(request, 'admin/register.html')

        # Crear usuario
        user = User.objects.create_user(username=email, email=email, password=password1)
        user.save()

        # Renderizamos la misma página con la modal activada
        return render(request, 'admin/register.html', {'messages_success': True})

    # GET request
    return render(request, 'admin/register.html')

#@login_required(login_url='login')
def inicio(request):
    return render(request, 'inicio.html')


@login_required
def finalizar_compra(request):
    # Aseguramos que la acción solo se ejecute al presionar el botón (método POST)
    if request.method == 'POST':
        try:
            # Usamos una transacción atómica para asegurar que todas las operaciones se completen
            # o que ninguna se ejecute (si falla algo en el medio).
            with transaction.atomic():
                # 1. Recuperar el Carrito y sus Ítems
                carrito = get_object_or_404(CarritoDeCompras, usuario=request.user)
                items_carrito = ItemCarrito.objects.filter(carrito=carrito).select_related('producto')

                if not items_carrito.exists():
                    # Si el carrito está vacío, no se puede finalizar la compra
                    return redirect('ver_carrito')

                    # 2. Calcular el valor total del pedido (Subtotal + Envío fijo, como en ver_carrito)
                subtotal = 0
                for item in items_carrito:
                    subtotal += item.cantidad * item.producto.valor_unitario

                # Definir valores fijos para el ejemplo
                costo_envio = 5.00
                valor_total_pagado = subtotal + costo_envio

                # 3. Crear el nuevo Pedido
                nuevo_pedido = Pedido.objects.create(
                    id_usuario=request.user,
                    valor_pagado=valor_total_pagado,
                    estado='PAGADO',  # Asumimos pago inmediato para este ejemplo
                    metodo_pago='Efectivo/Prueba',  # Define el método de pago
                    # is_combo, combo_opcional, id_producto_opcional se dejan por defecto (False/None)
                    # ya que estamos comprando desde la lista normal de productos.
                )

                # 4. Mover Ítems del Carrito al DetallePedido
                for item in items_carrito:
                    DetallePedido.objects.create(
                        pedido=nuevo_pedido,
                        producto=item.producto,
                        cantidad=item.cantidad,
                        # Usamos el precio unitario actual del producto para el historial
                        precio_item=item.producto.valor_unitario
                    )

                    # Opcional: Descontar stock (si lo necesitas)
                    # item.producto.stock -= item.cantidad
                    # item.producto.save()

                # 5. Vaciar el Carrito (Eliminar todos los ItemCarrito)
                items_carrito.delete()

                # Opcional: Puedes redirigir a una página de confirmación de pedido
                return redirect('pagina_confirmacion', pedido_id=nuevo_pedido.id)

        except CarritoDeCompras.DoesNotExist:
            # El usuario no tiene un carrito para finalizar
            return redirect('lista_productos')
        except IntegrityError:
            # Manejar errores de la base de datos (por ejemplo, si el stock es negativo, etc.)
            # Aquí podrías añadir lógica de logs o mensajes de error al usuario.
            return render(request, 'error_transaccion.html', {'mensaje': 'Ocurrió un error al procesar el pedido.'})

    return redirect('ver_carrito')  # Si alguien intenta acceder por GET, lo mandamos al carrito


@login_required
def pagina_confirmacion(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, id_usuario=request.user)
    contexto = {
        'pedido': pedido
    }
    return render(request, 'pedido/confirmacion.html', contexto)
