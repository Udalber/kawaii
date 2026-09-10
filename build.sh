#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Cargar automáticamente los 14 productos, categorías y combos iniciales
if [ -f "datos_iniciales.json" ]; then
    python manage.py loaddata datos_iniciales.json || true
fi

# Garantizar existencia del superusuario admin
python crear_admin.py
