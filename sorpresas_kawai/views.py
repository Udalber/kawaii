from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import Producto


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


def lista_productos(request):
    """
    Vista que recupera todos los productos y los pasa a la plantilla.
    """
    productos = Producto.objects.filter(activo=True).order_by("nombre")

    contexto = {
        "productos": productos,
        "titulo": "Nuestra Colección de Productos"
    }

    return render(request, "productos/lista.html", contexto)
