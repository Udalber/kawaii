# Documentación técnica — Sorpresas Kawaii

## 1. Descripción general

**Sorpresas Kawaii** es una aplicación web de comercio electrónico desarrollada con Django. Permite a los clientes explorar productos de papelería, combos y scoops/sorpresas, administrar su carrito de compras en tiempo real, finalizar pedidos con selección de método de pago, consultar su historial y seguimiento de pedidos, y recuperar su contraseña mediante correo electrónico.

La aplicación sigue la arquitectura **MVT** (Modelo - Vista - Template) de Django:

```text
Usuario → URL → Vista → Modelo/Base de datos → Plantilla HTML → Usuario
```

- **Modelo:** define las entidades de datos, relaciones y métodos auxiliares.
- **Vista:** procesa la lógica de negocio, autenticación, transacciones y respuesta HTTP.
- **Plantilla:** renderiza la interfaz HTML dinámica con diseño responsive y estética kawaii.

---

## 2. Tecnologías y herramientas

| Área | Tecnología | Uso en el proyecto |
| --- | --- | --- |
| **Backend** | Python 3.x | Lógica del servidor y reglas de negocio. |
| **Framework web** | Django 6.0 | Enrutamiento, vistas, ORM, sesiones, auth, mensajes y panel de administración. |
| **Base de datos** | SQLite (`db.sqlite3`) | Almacenamiento relacional de usuarios, perfiles, productos, combos, carritos y pedidos. |
| **Frontend** | HTML5 semántico | Estructura modular de páginas y partials reutilizables. |
| **Estilos** | CSS3 nativo (`kawaii_admin.css`) | Paleta de colores kawaii (pasteles), tipografía, diseño responsivo, cards y modales. |
| **Interactividad** | JavaScript (Vanilla) | Toggle de contraseñas, modales de autenticación y transiciones. |
| **Servicio de correo** | Gmail SMTP con TLS (puerto 587) | Envío automático de correos con enlaces y tokens seguros para restablecer contraseñas. |
| **Iconografía** | Font Awesome 6 (CDN) + SVG | Iconos sociales, iconos de interfaz y favicon personalizado en forma de nube. |

---

## 3. Librerías y módulos clave

### Django
- `django.db.models`: Definición de tablas, llaves foráneas, campos UUID, relaciones Many-to-Many con intermediarias y agregaciones (`Count`).
- `django.shortcuts`: Renderizado (`render`), redirecciones (`redirect`) y obtención de objetos (`get_object_or_404`).
- `django.contrib.auth`: Autenticación de usuarios (`login`, `logout`, `authenticate`, `User`).
- `django.contrib.auth.decorators.login_required`: Control de acceso a vistas privadas (carrito, checkout, historial).
- `django.contrib.auth.views`: Vistas genéricas de restablecimiento de contraseña (`PasswordResetView`, `PasswordResetConfirmView`, etc.).
- `django.contrib.messages`: Retroalimentación interactiva al usuario (éxito, error, advertencias).
- `django.db.transaction`: Transacciones atómicas (`@transaction.atomic`) para asegurar la consistencia al crear pedidos y vaciar carritos.

### Biblioteca estándar de Python
- `uuid`: Generación de claves primarias universales y códigos identificadores seguros.
- `os`: Lectura de variables de entorno seguras (`GMAIL_USER`, `GMAIL_APP_PASSWORD`).
- `pathlib.Path`: Resolución multiplataforma de rutas del proyecto.

---

## 4. Base de datos y modelos

El proyecto utiliza UUID como identificador primario en sus modelos para mayor seguridad y escalabilidad.

```text
┌──────────────┐         ┌──────────────┐         ┌─────────────────┐
│  Categoria   │ 1 ─── N │   Producto   │ 1 ─── N │ DetallePedido   │
└──────────────┘         └──────────────┘         └────────┬────────┘
                                │                          │
                                │ N                        │ N
                         ┌──────┴───────┐                  │
                         │ CombosProd.  │                  │
                         └──────┬───────┘                  │
                                │ N                        │
                                │                          │
┌──────────────┐         ┌──────┴───────┐                  │
│     User     │ 1 ─── N │    Combo     │ 1 ───────────────┤
└──────┬───────┘         └──────────────┘                  │
       │                                                   │
       ├───────── 1 ─── 1 ── UserProfile                   │
       │                                                   │
       ├───────── 1 ─── 1 ── CarritoDeCompras ── 1 ─── N ──┤ ItemCarrito
       │                                                   │
       └───────── 1 ─── N ── Pedido ─────────── 1 ─── N ───┘
```

### Entidades detalladas:

1. **`User` / `UserProfile`**:
   - `User`: Modelo estándar de Django (nombre de usuario, correo, contraseña cifrada).
   - `UserProfile`: Relación 1 a 1 para guardar dirección de envío u otros datos del cliente.
2. **`Categoria`**: Clasificación de productos (Papelería, Accesorios, etc.).
3. **`Producto`**:
   - Campos: `nombre`, `descripcion`, `valor_unitario`, `descuento_porcentaje`, `stock`, `imagen`, `imagen_url`, `activo`.
   - Propiedades: `precio_final` (calcula el descuento aplicado), `get_imagen_url`.
4. **`Combo`**:
   - Campos: `nombre`, `descripcion`, `imagen`, `imagen_url`, `valor_combo`, `descuento_porcentaje`, `numero_productos`, `activo`.
   - Relación M2M con `Producto` mediante la tabla intermedia `CombosProductos`.
5. **`CombosProductos`**: Almacena los productos específicos y la cantidad de cada uno contenida en un combo.
6. **`CarritoDeCompras` & `ItemCarrito`**:
   - Cada usuario registrado posee un único carrito persistente.
   - Soporta ítems de tipo producto individual o tipo combo con control de cantidades.
7. **`Pedido`**:
   - Registra compras generadas: `id_usuario`, `fecha_pedido`, `valor_pagado`, `metodo_pago`, `detalle_pago`, `estado` (`PENDIENTE`, `PAGADO`, `ENVIADO`, `ENTREGADO`, `CANCELADO`).
   - Gestión logística: `empresa_envio`, `numero_guia` y `comprobante_pago`.
   - Propiedad `codigo_pedido`: Genera un identificador visual amigable (ej. `#SK-A1B2C3`).
8. **`DetallePedido`**: Desglose de productos/combos, cantidades y precios históricos al momento de la compra.

---

## 5. Estructura de carpetas del proyecto

```text
kawaii/
├── manage.py                          # Gestor de comandos de Django
├── db.sqlite3                         # Base de datos SQLite local
├── DOCUMENTACION_TECNICA.md           # Documentación técnica completa
├── settings/
│   ├── settings.py                    # Configuración global, apps, BD, SMTP, estáticos
│   └── urls.py                        # Enrutador principal del proyecto
├── sorpresas_kawai/
│   ├── admin.py                       # Configuración y personalización del Django Admin
│   ├── models.py                      # Definición de todos los modelos del sistema
│   ├── views.py                       # Controladores y lógica de vistas
│   ├── urls.py                        # Rutas de la aplicación de tienda
│   └── migrations/                    # Historial de migraciones del esquema
├── templates/
│   ├── base.html                      # Layout maestro con cabecera, estilos y scripts
│   ├── Inicio.html                    # Página de inicio con banners y novedades
│   ├── sobre_nosotros.html            # Sección institucional y redes sociales
│   ├── partials/
│   │   ├── navbar.html                # Barra de navegación compartida con contador de carrito
│   │   └── footer.html                # Pie de página global
│   ├── admin/
│   │   ├── logintest.html             # Pantalla de inicio de sesión de clientes
│   │   └── register.html              # Pantalla de registro de nuevas cuentas
│   ├── productos/
│   │   ├── lista.html                 # Catálogo general con filtros por categoría
│   │   ├── combos.html                # Catálogo de combos preparados
│   │   └── sorpresas.html             # Sección de scoops y sorpresas kawaii
│   ├── carrito/
│   │   └── detalle.html               # Resumen del carrito, selector de envío y checkout
│   ├── pedido/
│   │   ├── confirmacion.html          # Confirmación con datos de transferencia y pago
│   │   └── mis_pedidos.html           # Panel de historial y seguimiento de pedidos
│   └── registration/                  # Flujo completo de recuperación de contraseña
│       ├── password_reset_form.html   # Formulario para ingresar correo
│       ├── password_reset_done.html   # Aviso de correo enviado
│       ├── password_reset_email.html  # Cuerpo HTML del correo con el enlace seguro
│       ├── password_reset_subject.txt # Asunto del correo
│       ├── password_reset_confirm.html# Formulario para definir nueva contraseña
│       └── password_reset_complete.html# Confirmación de contraseña actualizada
└── static/
    ├── css/
    │   └── kawaii_admin.css           # Hoja de estilos principal y utilidades
    └── img/
        ├── favicon.svg                # Favicon SVG (nube kawaii)
        ├── hero_kawaii.jpg            # Banner de bienvenida
        └── placeholder.png            # Imagen por defecto para productos sin foto
```

---

## 6. Módulos y funcionalidades principales

### 🛍️ Catálogo y navegación
- **Productos:** Filtros dinámicos por categoría con conteo de existencias y botón directo de compra.
- **Combos:** Listado de packs especiales con desglose de ítems incluidos y cálculo automático de descuentos.
- **Sorpresas / Scoops:** Presentación de scoops temáticos con animaciones y selección de tamaño.
- **Sobre Nosotros:** Página informativa con enlace directo a Instagram y TikTok.

### 🛒 Carrito de compras y Checkout
- Soporta tanto productos individuales como combos simultáneamente.
- Modificación en vivo de cantidades (+ / -) o eliminación directa de ítems.
- Cálculo de subtotal, costo de envío ($10,000 COP) y total final.
- **Procesamiento de pedidos:** Ejecución atómica (`@transaction.atomic`) para garantizar que la creación del pedido, el desglose en `DetallePedido` y el vaciado del carrito se ejecuten sin inconsistencias.

### 📦 Gestión y seguimiento de pedidos
- **Pantalla de Confirmación:** Brinda al usuario su código de pedido (`#SK-XXXXXX`), datos de cuentas Nequi/Daviplata/Bancolombia y enlace para adjuntar o reportar el comprobante.
- **Mis Pedidos (`/mis-pedidos/`):** Vista privada donde cada cliente puede revisar sus compras históricas, estados en tiempo real (Pendiente, Pagado, Enviado, Entregado) y guías de transporte con transportadora asignada.

### 🔐 Autenticación y seguridad
- Registro de cuentas con validación de contraseñas y unicidad de correo.
- Inicio de sesión con persistencia mediante sesiones seguras de Django.
- Cierre de sesión protegido contra métodos no autorizados.
- **Recuperación de contraseña:** Flujo oficial de Django con tokens criptográficos de un solo uso enviados por correo SMTP.

### ⚙️ Panel de administración personalizado
- Registro completo de modelos con filtros, búsquedas y columnas informativas (`admin.py`).
- Capacidad de asignar empresa de transporte y número de guía directamente desde el admin para que el cliente lo visualice al instante en `Mis Pedidos`.

---

## 7. Mapa de rutas (Endpoints)

| URL | Nombre de Ruta | Descripción | Acceso |
| --- | --- | --- | --- |
| `/` | `inicio` | Landing page principal | Público |
| `/productos/` | `lista_productos` | Catálogo de productos con filtros | Público |
| `/combos/` | `lista_combos` | Catálogo de combos | Público |
| `/sorpresa/` | `lista_sorpresas` | Sección de sorpresas y scoops | Público |
| `/sobre-nosotros/` | `sobre_nosotros` | Información de la marca y redes sociales | Público |
| `/register/` | `register` | Formulario de registro de usuarios | Público |
| `/login/` | `login` | Inicio de sesión | Público |
| `/logout/` | `logout` | Cierre de sesión | Autenticado |
| `/carrito/` | `ver_carrito` | Vista del carrito de compras | Autenticado |
| `/agregar/<uuid>/` | `agregar_a_carrito` | Agregar/incrementar producto | Autenticado |
| `/quitar/<uuid>/` | `quitar_de_carrito` | Disminuir/eliminar producto | Autenticado |
| `/combos/agregar/<uuid>/` | `agregar_combo_a_carrito` | Agregar combo al carrito | Autenticado |
| `/combos/quitar/<uuid>/` | `quitar_combo_de_carrito` | Disminuir combo del carrito | Autenticado |
| `/carrito/finalizar/` | `finalizar_compra` | Procesar orden y vaciar carrito | Autenticado |
| `/pedido/confirmacion/<uuid>/`| `pagina_confirmacion` | Pantalla de confirmación y datos de pago | Autenticado |
| `/mis-pedidos/` | `mis_pedidos` | Historial y rastreo de envíos del cliente | Autenticado |
| `/recuperar-contrasena/` | `password_reset` | Formulario para solicitar reseteo | Público |
| `/recuperar-contrasena/enviada/` | `password_reset_done` | Confirmación de correo enviado | Público |
| `/restablecer-contrasena/<uid>/<token>/` | `password_reset_confirm` | Formulario con token para nueva clave | Público |
| `/restablecer-contrasena/listo/` | `password_reset_complete` | Éxito tras actualizar contraseña | Público |

---

## 8. Configuración de variables de entorno

Para el funcionamiento del envío de correos por Gmail SMTP, configure las siguientes variables en su entorno del sistema:

```bash
GMAIL_USER="tucorreo@gmail.com"
GMAIL_APP_PASSWORD="tu_contraseña_de_aplicacion_de_16_caracteres"
```

> **Nota:** La contraseña debe generarse en la consola de seguridad de Google ("Contraseñas de aplicación"), no es la contraseña habitual de la cuenta.

---

## 9. Guía de ejecución en desarrollo

1. **Clonar el repositorio y situarse en la carpeta:**
   ```powershell
   cd kawaii
   ```
2. **Aplicar migraciones:**
   ```powershell
   python manage.py migrate
   ```
3. **Crear usuario administrador (opcional):**
   ```powershell
   python manage.py createsuperuser
   ```
4. **Iniciar el servidor local:**
   ```powershell
   python manage.py runserver
   ```
5. **Abrir en el navegador:**
   - Tienda: `http://127.0.0.1:8000/`
   - Panel de Administración: `http://127.0.0.1:8000/admin/`

---

## 10. Consideraciones para despliegue a producción

- [ ] Establecer `DEBUG = False` en `settings.py`.
- [ ] Configurar `ALLOWED_HOSTS` con los dominios o subdominios autorizados.
- [ ] Exportar `SECRET_KEY` a una variable de entorno.
- [ ] Utilizar un motor de base de datos como PostgreSQL o MySQL para entornos de alta concurrencia.
- [ ] Configurar un servidor web para archivos estáticos y media (WhiteNoise, AWS S3 o Nginx).
- [ ] Habilitar certificados SSL/HTTPS obligatorio (`SECURE_SSL_REDIRECT = True`).
