from django.urls import path
from .views.home_views import *
from .views.usuario_views import *
from .views.monitor_views import *
from .views.sala_views import *
from .views.actividad_views import *

urlpatterns = [
    # HOME
    path('', home_views, name='home_administracion'),

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
    path('monitor/', listar_monitores, name='listar_monitor'),
    path('monitores/nuevo/', formulario_registro_monitor, name='registrar_monitores'),
    path('monitores/<int:id>/', filtrar_monitor_id, name='filtrar_monitor'),
    path('monitores/<int:id>/editar/', editar_monitor_id, name='editar_monitor'),
    path('monitores/<int:id>/eliminar/', confirmar_eliminar_monitor, name='confirmar_eliminar_monitor'),

    #SALAS
    #Consulta de salas
    path('salas/', listar_salas, name='listar_salas'),
    path('salas/nuevo/', formulario_registro_sala, name='registrar_salas'),
    path('salas/<int:id>/', filtrar_sala_id, name='filtrar_sala'),
    path('salas/<int:id>/editar/', editar_sala_id, name='editar_sala'),
    path('salas/<int:id>/eliminar/', confirmar_eliminar_sala, name='confirmar_eliminar_sala'),

    #ACTIVIDADES
    #Consulta de actividades
    path('actividades/', listar_actividades, name='listar_actividades'),
    path('actividades/nuevo/', formulario_registro_actividad, name='registrar_actividades'),
    path('actividades/<int:id>/', filtrar_actividad_id, name='filtrar_actividad'),
    path('actividades/<int:id>/editar/', editar_actividad_id, name='editar_actividad'),
    path('actividades/<int:id>/eliminar/', confirmar_eliminar_actividad, name='confirmar_eliminar_actividad')
]
