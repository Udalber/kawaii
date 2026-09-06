# Documentación técnica — Sorpresas Kawaii

## 1. Descripción general

**Sorpresas Kawaii** es una aplicación web de comercio electrónico. Permite consultar productos y combos, crear una cuenta, iniciar sesión, administrar un carrito de compras, confirmar pedidos y recuperar la contraseña por correo electrónico.

La aplicación sigue el patrón **MVT** de Django:

```text
Usuario → URL → Vista → Modelo/Base de datos → Plantilla HTML → Usuario
```

- **Modelo:** representa los datos y sus relaciones.
- **Vista:** contiene la lógica que responde a una petición.
- **Plantilla:** genera la interfaz HTML que se muestra en el navegador.

## 2. Tecnologías utilizadas

| Área | Tecnología | Uso en el proyecto |
| --- | --- | --- |
| Lenguaje backend | Python | Lógica de negocio y configuración. |
| Framework web | Django | Rutas, vistas, modelos, sesiones, autenticación, panel administrador y formularios. |
| Base de datos | SQLite | Almacenamiento local de usuarios, productos, carritos y pedidos. |
| Frontend | HTML5 | Estructura de las páginas. |
| Estilos | CSS3 | Diseño, paleta kawaii, tarjetas, formularios y navegación. |
| Interactividad | JavaScript | Mostrar u ocultar campos de contraseña y modal de registro. |
| Correo | Gmail SMTP con TLS | Envío de enlaces de recuperación de contraseña. |
| Recursos externos | Font Awesome por CDN | Iconos de redes sociales en la sección “Sobre nosotros”. |
| Icono de pestaña | SVG | Favicon personalizado con las iniciales SK. |

## 3. Librerías y módulos

### Django

El proyecto fue creado con Django 6.0. Los módulos de Django usados incluyen:

| Módulo | Propósito |
| --- | --- |
| `django.db.models` | Define tablas, campos y relaciones de la base de datos. |
| `django.shortcuts` | Renderiza plantillas y hace redirecciones. |
| `django.contrib.auth` | Autenticación, inicio y cierre de sesión. |
| `django.contrib.auth.models.User` | Usuarios registrados en la tienda. |
| `django.contrib.auth.decorators.login_required` | Protege vistas que requieren sesión iniciada. |
| `django.contrib.auth.forms.SetPasswordForm` | Formulario seguro para crear una contraseña nueva. |
| `django.contrib.auth.views` | Recuperación de contraseña mediante `PasswordResetView` y vistas relacionadas. |
| `django.contrib.messages` | Mensajes de validación del registro. |
| `django.db.transaction` | Procesamiento atómico al finalizar una compra. |
| `django.db.models.Count` | Conteo de productos por categoría. |

### Biblioteca estándar de Python

| Módulo | Propósito |
| --- | --- |
| `uuid` | Genera identificadores únicos para varias tablas. |
| `os` | Lee variables de entorno para las credenciales de Gmail. |
| `pathlib.Path` | Construye rutas del proyecto de forma segura. |

No existe actualmente un archivo `requirements.txt`; la dependencia externa principal es **Django**. Si el proyecto se va a compartir o desplegar, conviene crear dicho archivo con las versiones instaladas.

## 4. Base de datos

La aplicación usa SQLite, configurada en `settings/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

El archivo físico de la base es `db.sqlite3`, ubicado en la raíz del proyecto.

### Entidades principales

| Modelo | Descripción |
| --- | --- |
| `User` | Usuario estándar proporcionado por Django. Guarda usuario, correo y contraseña cifrada. |
| `UserProfile` | Información adicional del usuario, como dirección de envío. |
| `Categoria` | Agrupa los productos por categoría. |
| `Producto` | Producto disponible: nombre, descripción, precio, stock, imagen y estado activo. |
| `Combo` | Conjunto de productos con precio y descuento opcional. |
| `CombosProductos` | Tabla intermedia que indica qué productos y cantidades contiene un combo. |
| `CarritoDeCompras` | Un carrito asociado a cada usuario. |
| `ItemCarrito` | Producto o combo y su cantidad dentro del carrito. |
| `Pedido` | Compra realizada por un usuario. Guarda estado, fecha, valor pagado y método de pago. |
| `DetallePedido` | Cada ítem comprado dentro de un pedido. |

Las relaciones importantes son:

```text
Categoría 1 ─── N Producto
Usuario    1 ─── 1 CarritoDeCompras
Carrito    1 ─── N ItemCarrito
Usuario    1 ─── N Pedido
Pedido     1 ─── N DetallePedido
Combo      N ─── N Producto (mediante CombosProductos)
```

## 5. Estructura principal de carpetas

```text
kawaii/
├── manage.py                     # Comandos de administración de Django
├── db.sqlite3                    # Base de datos SQLite
├── settings/
│   ├── settings.py               # Configuración general
│   └── urls.py                   # Rutas globales
├── sorpresas_kawai/
│   ├── models.py                 # Modelos de la base de datos
│   ├── views.py                  # Lógica de las páginas
│   ├── urls.py                   # Rutas de la aplicación
│   ├── admin.py                  # Configuración del panel administrador
│   └── migrations/               # Historial de cambios de la base
├── templates/                    # Plantillas HTML
│   ├── admin/                    # Login y registro
│   ├── productos/                # Catálogo y combos
│   ├── carrito/                  # Carrito de compras
│   ├── pedido/                   # Confirmación de pedido
│   ├── registration/             # Recuperación de contraseña
│   └── partials/navbar.html      # Barra de navegación reutilizable
└── static/
    ├── css/kawaii_admin.css      # Estilos principales
    └── img/favicon.svg           # Icono de pestaña
```

## 6. Funcionalidades implementadas

### Catálogo

- Muestra productos activos.
- Permite filtrar por categoría.
- Muestra la cantidad de cada producto que ya está en el carrito.

### Combos

- Lista combos activos.
- Muestra productos incluidos, descuento y precio.
- Permite agregar o quitar combos del carrito.

### Usuarios y seguridad

- Registro de usuarios con correo y contraseña.
- Inicio y cierre de sesión mediante sesiones de Django.
- Protección de rutas como carrito y finalización de compra con `@login_required`.
- Contraseñas almacenadas mediante hash; nunca como texto visible.
- Recuperación de contraseña con un token temporal enviado por correo.

### Carrito y pedidos

- Un carrito por usuario.
- Agregar, incrementar, disminuir o eliminar productos y combos.
- Cálculo de subtotal, envío y total.
- Creación de pedido y detalles de pedido al finalizar compra.
- Uso de transacción atómica para evitar pedidos incompletos ante un error.

### Interfaz

- Barra de navegación reutilizable en `templates/partials/navbar.html`.
- Estados vacíos para carrito, productos y combos.
- Página “Sobre nosotros” con espacios para enlaces de TikTok e Instagram.
- Favicon en forma de nube con las iniciales SK.

## 7. Rutas destacadas

| Ruta | Nombre | Función |
| --- | --- | --- |
| `/` | `inicio` | Página principal. |
| `/productos/` | `lista_productos` | Catálogo de productos. |
| `/combos/` | `lista_combos` | Catálogo de combos. |
| `/carrito/` | `ver_carrito` | Carrito del usuario autenticado. |
| `/register/` | `register` | Registro de cuentas. |
| `/login/` | `login` | Inicio de sesión. |
| `/logout/` | `logout` | Cierre de sesión. |
| `/recuperar-contrasena/` | `password_reset` | Solicitud de recuperación de contraseña. |
| `/sobre-nosotros/` | `sobre_nosotros` | Información de la tienda y redes sociales. |

## 8. Correo para recuperación de contraseña

La aplicación usa el servidor SMTP de Gmail con TLS en el puerto 587. Las credenciales no están escritas en el proyecto; se obtienen desde variables de entorno:

```text
GMAIL_USER
GMAIL_APP_PASSWORD
```

`GMAIL_APP_PASSWORD` debe ser una contraseña de aplicación de Gmail, no la contraseña normal de la cuenta.

## 9. Ejecución local

Desde la raíz del proyecto:

```powershell
py manage.py runserver
```

La aplicación normalmente queda disponible en:

```text
http://127.0.0.1:8000/
```

Comandos útiles:

```powershell
py manage.py makemigrations
py manage.py migrate
py manage.py createsuperuser
py manage.py runserver
```

## 10. Recomendaciones antes de publicar

- Cambiar `DEBUG = True` a `False`.
- Configurar `ALLOWED_HOSTS` con el dominio real.
- Mover `SECRET_KEY` a una variable de entorno.
- Mantener las credenciales de Gmail fuera del código.
- Crear `requirements.txt` para registrar dependencias.
- Considerar PostgreSQL en lugar de SQLite si habrá muchos usuarios o pedidos simultáneos.
- Usar HTTPS en producción, especialmente porque existen usuarios y recuperación de contraseñas.
