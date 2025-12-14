from django.urls import path
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from . import views

urlpatterns = [

path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('', views.inicio, name='inicio'),
    path('productos/', views.lista_productos, name='lista_productos'),
    ]