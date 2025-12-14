from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import Producto, Categoria, CarritoDeCompras, ItemCarrito


def login_view(request):
    """
    Login custom que autentica contra Django y permite acceso al admin
    """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("/admin/")  # 🔥 entra directo al admin
        else:
            return render(
                request,
                "admin/logintest.html",
                {"error": "Usuario o contraseña incorrectos"}
            )

    return render(request, "admin/logintest.html")


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
    costo_envio = 5.00

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

