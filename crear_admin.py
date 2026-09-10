import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.settings')
django.setup()

from django.contrib.auth.models import User

username = os.environ.get('ADMIN_USERNAME', 'admin')
email = os.environ.get('ADMIN_EMAIL', 'admin@sorpresaskawaii.com')
password = os.environ.get('ADMIN_PASSWORD', '')

if not User.objects.filter(username=username).exists():
    pass_to_use = password if password else 'Admin2026!#Kawaii'
    User.objects.create_superuser(username=username, email=email, password=pass_to_use)
    print(f"Superusuario '{username}' creado con éxito.")
elif password:
    user = User.objects.get(username=username)
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print(f"Contraseña actualizada para superusuario '{username}'.")
else:
    print(f"Superusuario '{username}' ya existe en el sistema.")
