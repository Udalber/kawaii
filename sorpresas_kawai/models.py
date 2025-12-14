import uuid
from django.db import models
from django.contrib.auth import get_user_model

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
    stock = models.IntegerField(default=0)
    imagen_url = models.URLField(max_length=700, blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return self.nombre


class Combo(models.Model):
    """
    Corresponde a la entidad 'Combos'.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=255, default="Combo", null=True)
    productos = models.ManyToManyField(
        Producto,
        through='CombosProductos',
        related_name='combos'
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
        return f"Combo {self.id}"


class CombosProductos(models.Model):
    """
    Tabla intermedia para la relación N:M entre Combo y Producto. 
    Representa la 'lista_id_productos: array[uuid]' en tu diagrama de Combos.
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

    def __str__(self):
        return f"Pedido {self.id} de {self.id_usuario.username}"


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
            f"Combo {self.combo.id}" if self.combo else "Ítem Desconocido")
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
    Representa un producto específico dentro de un carrito.
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
        return f"{self.cantidad} x {self.producto.nombre}"
