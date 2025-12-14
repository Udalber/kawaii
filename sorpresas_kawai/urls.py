from django.urls import path
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from . import views

urlpatterns = [

    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('', views.inicio, name='inicio'),
    path('productos/', views.lista_productos, name='lista_productos'),
    path('login/', views.login_view, name='login'),
    path('agregar/<uuid:producto_id>/', views.agregar_a_carrito, name='agregar_a_carrito'),
    path('quitar/<uuid:producto_id>/', views.quitar_de_carrito, name='quitar_de_carrito'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/finalizar/', views.finalizar_compra, name='finalizar_compra'),
    path('pedido/confirmacion/<uuid:pedido_id>/', views.pagina_confirmacion, name='pagina_confirmacion'),
]
