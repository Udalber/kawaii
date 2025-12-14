from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
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

