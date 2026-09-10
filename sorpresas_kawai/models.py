import uuid
import re
import urllib.parse
from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()



class Categoria(models.Model):
    """
    Corresponde a la entidad 'Categoria'.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre


class UserProfile(models.Model):
    """
    Extiende el modelo 'User' de Django.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    direccion_envio = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"

    def __str__(self):
        return f"Perfil de {self.user.username}"


class Producto(models.Model):
    """
    Corresponde a la entidad 'Producto'.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        related_name='productos',
        null=True,
        blank=True
    )
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    valor_unitario = models.FloatField()
    descuento_porcentaje = models.FloatField(default=0.0)
    stock = models.IntegerField(default=0)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    imagen_url = models.URLField(max_length=700, blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return self.nombre

    @property
    def get_imagen_url(self):
        if self.imagen:
            return self.imagen.url
        if self.imagen_url:
            return self.imagen_url
        return None

    @property
    def precio_final(self):
        if self.descuento_porcentaje and self.descuento_porcentaje > 0:
            return round(self.valor_unitario * (1 - (self.descuento_porcentaje / 100)), 2)
        return self.valor_unitario


class Combo(models.Model):
    """
    Corresponde a la entidad 'Combos'.
    Permite crear combos de manera directa (nombre, descripción, imagen, precio)
    y opcionalmente vincular productos que lo componen.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=255, default="Combo", null=True)
    descripcion = models.TextField(blank=True, null=True)
    imagen = models.ImageField(upload_to='combos/', blank=True, null=True)
    imagen_url = models.URLField(max_length=700, blank=True, null=True)
    productos = models.ManyToManyField(
        Producto,
        through='CombosProductos',
        related_name='combos',
        blank=True
    )
    usuario_id = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='combos_creados',
        null=True,
        blank=True
    )
    numero_productos = models.IntegerField(default=0)
    descuento_porcentaje = models.FloatField(default=0.0)
    valor_combo = models.FloatField()
    valido_hasta = models.DateField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Combo"
        verbose_name_plural = "Combos"

    def __str__(self):
        return self.nombre if self.nombre else f"Combo {self.id}"

    @property
    def get_imagen_url(self):
        if self.imagen:
            return self.imagen.url
        if self.imagen_url:
            return self.imagen_url
        return None

    @property
    def precio_final(self):
        if self.descuento_porcentaje and self.descuento_porcentaje > 0:
            return round(self.valor_combo * (1 - (self.descuento_porcentaje / 100)), 2)
        return self.valor_combo


class CombosProductos(models.Model):
    """
    Tabla intermedia para la relación N:M entre Combo y Producto. 
    Representa la lista de productos y cantidades incluidas en un Combo.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    combo = models.ForeignKey(Combo, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveSmallIntegerField(default=1)

    class Meta:
        unique_together = ('combo', 'producto')
        verbose_name = "Producto en Combo"
        verbose_name_plural = "Productos en Combos"


class Pedido(models.Model):
    """
    Corresponde a la entidad 'Pedido'.
    """
    ESTADOS = [
        ('PENDIENTE', 'Pendiente de Pago'),
        ('PAGADO', 'Pagado'),
        ('ENVIADO', 'Enviado'),
        ('ENTREGADO', 'Entregado'),
        ('CANCELADO', 'Cancelado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    id_usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='pedidos'
    )

    fecha_pedido = models.DateTimeField(auto_now_add=True)
    valor_pagado = models.FloatField()
    estado = models.CharField(max_length=50, choices=ESTADOS, default='PENDIENTE')
    metodo_pago = models.CharField(max_length=100)
    detalle_pago = models.TextField(blank=True, null=True)
    comprobante_pago = models.ImageField(upload_to='comprobantes/', blank=True, null=True, verbose_name="Comprobante de Pago")
    empresa_envio = models.CharField(max_length=100, blank=True, null=True, verbose_name="Empresa de Envío")
    numero_guia = models.CharField(max_length=100, blank=True, null=True, verbose_name="Número de Guía")

    is_combo = models.BooleanField(default=False)
    combo_opcional = models.ForeignKey(
        Combo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pedidos_combo'
    )
    id_producto_opcional = models.ForeignKey(
        Producto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pedidos_producto'
    )
    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    @property
    def codigo_pedido(self):
        """Genera un código simplificado, profesional y legible (ej: #SK-849201)."""
        clean_hex = str(self.id).replace('-', '').upper()
        return f"#SK-{clean_hex[:6]}"

    def generar_mensaje_whatsapp(self):
        """
        Genera el texto preformateado para WhatsApp con el ID del pedido,
        nombre del cliente, lista de artículos comprados y total.
        """
        nombre_cliente = self.id_usuario.first_name or self.id_usuario.username
        items_lista = []

        for d in self.detalles.all():
            nombre_item = d.producto.nombre if d.producto else (
                d.combo.nombre if d.combo else 'Item'
            )
            items_lista.append(f"- {d.cantidad}x {nombre_item} (${d.precio_item:,.0f} COP c/u)")

        if not items_lista:
            if self.combo_opcional:
                items_lista.append(f"- 1x {self.combo_opcional.nombre}")
            elif self.id_producto_opcional:
                items_lista.append(f"- 1x {self.id_producto_opcional.nombre}")

        items_str = "\n".join(items_lista) if items_lista else "- Articulos registrados en el sistema"

        lineas = [
            "Hola, acabo de realizar una compra en Sorpresas Kawaii.",
            "",
            f"*Pedido:* {self.codigo_pedido}",
            f"*Cliente:* {nombre_cliente}",
            f"*Total a pagar:* ${self.valor_pagado:,.0f} COP",
            f"*Estado:* {self.get_estado_display()}",
            "",
            "*Articulos incluidos:*",
            items_str,
            "",
            "espero de sus indicaciones para coordinar el pago y envio. Muchas gracias."
        ]
        return "\n".join(lineas)


    @property
    def whatsapp_url(self):
        """
        Genera el enlace universal de WhatsApp con el número oficial y el mensaje codificado.
        """
        phone = getattr(settings, 'WHATSAPP_PHONE_NUMBER', '573222385508')
        phone_clean = re.sub(r'\D', '', str(phone))
        mensaje = self.generar_mensaje_whatsapp()
        return f"https://wa.me/{phone_clean}?text={urllib.parse.quote(mensaje)}"

    def save(self, *args, **kwargs):
        """
        Sobrescribe save para detectar cambios en el estado del pedido o información de guía
        y disparar el correo de notificación al cliente de forma automática.
        """
        is_new = self.pk is None
        old_estado = None
        old_empresa = None
        old_guia = None

        if not is_new:
            prev = Pedido.objects.filter(pk=self.pk).values('estado', 'empresa_envio', 'numero_guia').first()
            if prev:
                old_estado = prev.get('estado')
                old_empresa = prev.get('empresa_envio')
                old_guia = prev.get('numero_guia')

        super().save(*args, **kwargs)

        if not is_new and old_estado is not None:
            estado_cambio = old_estado != self.estado
            guia_cambio = (self.estado in ('ENVIADO', 'ENTREGADO')) and (
                (bool(self.numero_guia) and self.numero_guia != old_guia) or
                (bool(self.empresa_envio) and self.empresa_envio != old_empresa)
            )

            if estado_cambio or guia_cambio:
                try:
                    from .emails import enviar_correo_actualizacion_pedido
                    enviar_correo_actualizacion_pedido(
                        self,
                        estado_anterior=old_estado,
                        info_rastreo_actualizada=guia_cambio and not estado_cambio
                    )
                except Exception:
                    pass

    def __str__(self):
        return f"Pedido {self.codigo_pedido} - {self.id_usuario.username}"



class DetallePedido(models.Model):
    """
    Tabla de detalle de ítems para el Pedido (práctica recomendada).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    combo = models.ForeignKey(
        Combo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    cantidad = models.PositiveIntegerField(default=1)
    precio_item = models.FloatField()

    class Meta:
        verbose_name = "Detalle de Pedido"
        verbose_name_plural = "Detalles de Pedidos"

    def __str__(self):
        item_nombre = self.producto.nombre if self.producto else (
            self.combo.nombre if (self.combo and self.combo.nombre) else (
                f"Combo {self.combo.id}" if self.combo else "Ítem Desconocido"
            )
        )
        return f"{self.cantidad} x {item_nombre} en Pedido {self.pedido.id}"


class CarritoDeCompras(models.Model):
    """
    Representa el carrito de compras de un usuario.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='carrito'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Carrito de {self.usuario.username}"


class ItemCarrito(models.Model):
    """
    Representa un producto o combo específico dentro de un carrito.
    """
    carrito = models.ForeignKey(
        CarritoDeCompras,
        on_delete=models.CASCADE,
        related_name='items'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    combo = models.ForeignKey(
        Combo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    cantidad = models.IntegerField(default=1)
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        nombre = self.producto.nombre if self.producto else (
            self.combo.nombre if (self.combo and self.combo.nombre) else (
                f"Combo {self.combo.id}" if self.combo else "Ítem"
            )
        )
        return f"{self.cantidad} x {nombre}"
