from django.urls import path
from . import views

urlpatterns = [
    path('productos/', views.lista_productos, name='lista_productos'),
    path('', views.lista_productos, name='lista_productos'),
    path('login/', views.login_view, name='login'),
    path('agregar/<uuid:producto_id>/', views.agregar_a_carrito, name='agregar_a_carrito'),
    path('quitar/<uuid:producto_id>/', views.quitar_de_carrito, name='quitar_de_carrito'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
]