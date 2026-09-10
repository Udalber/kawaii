"""
WSGI config for settings project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.settings')

application = get_wsgi_application()

# Inicialización automática de base de datos y datos en entornos como Render
try:
    from django.core.management import call_command
    from django.contrib.auth.models import User
    from sorpresas_kawai.models import Producto

    # 1. Asegurar que las migraciones estén aplicadas
    call_command('migrate', interactive=False)

    # 2. Si la base de datos está vacía, cargar el catálogo completo
    if Producto.objects.count() == 0:
        call_command('loaddata', 'datos_iniciales.json')
        print("Catálogo de 14 productos y categorías cargado con éxito en Render.")

    # 3. Asegurar la existencia del superusuario admin
    username = os.environ.get('ADMIN_USERNAME', 'admin')
    password = os.environ.get('ADMIN_PASSWORD', 'Admin2026!#Kawaii')
    email = os.environ.get('ADMIN_EMAIL', 'admin@sorpresaskawaii.com')

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Superusuario '{username}' creado automáticamente en Render.")
    elif os.environ.get('ADMIN_PASSWORD'):
        user = User.objects.get(username=username)
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        print(f"Contraseña actualizada para superusuario '{username}'.")
except Exception as e:
    print(f"Nota en inicialización automática WSGI: {e}")
