from django.urls import path
from .views.usuario_views import *

urlpatterns = [
    #USUARIOS
    #Consulta de usuarios
    path('usuarios', listar_usuarios, name='listar_usuarios'),
    path('usuarios/nuevo/', formulario_registro_usuario, name='registrar_usuarios'),
    path('usuarios/<int:id>/', filtrar_usuario_id, name='filtrar_usuario'),
    path('usuarios/<int:id>/editar/', editar_usuario_id, name='editar_usuario'),
    path('usuarios/<int:id>/eliminar/', eliminar_usuario_id, name='eliminar_usuario')
]