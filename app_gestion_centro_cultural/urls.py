from django.urls import path
from .views.usuario_views import *
from .views.monitor_views import *

urlpatterns = [
    #USUARIOS
    #Consulta de usuarios
    path('usuarios/', listar_usuarios, name='listar_usuarios'),
    path('usuarios/nuevo/', formulario_registro_usuario, name='registrar_usuarios'),
    path('usuarios/<int:id>/', filtrar_usuario_id, name='filtrar_usuario'),
    path('usuarios/<int:id>/editar/', editar_usuario_id, name='editar_usuario'),
    path('usuarios/<int:id>/eliminar/', confirmar_eliminar_usuario, name='confirmar_eliminar_usuario'),
    
    #MONITORES
    #Consulta de monitores
    path('monitores/', listar_monitores, name='listar_monitores'),
    path('monitores/nuevo/', formulario_registro_monitor, name='registrar_monitores'),
    path('monitores/<int:id>/', filtrar_monitor_id, name='filtrar_monitor'),
    path('monitores/<int:id>/editar/', editar_monitor_id, name='editar_monitor'),
    path('monitores/<int:id>/eliminar/', confirmar_eliminar_monitor, name='confirmar_eliminar_monitor')
]