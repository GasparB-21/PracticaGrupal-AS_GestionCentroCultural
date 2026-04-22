from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from ..models import Usuario
from ..forms import UsuarioForm

# Consulta de usuarios
def listar_usuarios(request):
    if request.method != "GET":
        return JsonResponse({"error": "Método no permitido"}, status=405)
    
    listar_usuarios = Usuario.objects.all()
    dirUsuarios = {'usuarios': listar_usuarios}
    return render(request, 'app_gestion_centro_cultural/usuarios/lista_usuarios.html', dirUsuarios)

# Registar un nuevo usuario
def formulario_registro_usuario(request):
    #Comprobamos si se esta accediendo al formulario o si ya se ha mandado con la información
    if request.method == 'POST':
        #Creamos un form con los datos recibidos
        form = UsuarioForm(request.POST)
        #Validamos los datos recibidos
        if form.is_valid():
            form.save()
            return redirect('listar_usuarios')
        return render(request, 'app_gestion_centro_cultural/shared/formulario_registro.html', {'titulo': 'Página de registro de usuarios', 'form': form})
    else:
        form = UsuarioForm()
        return render(request, 'app_gestion_centro_cultural/shared/formulario_registro.html', {'titulo': 'Página de registro de usuarios', 'form': form})

# Filtrar usuario por id
def filtrar_usuario_id(request, id):
    if request.method != "GET":
        return JsonResponse({"error": "Método no permitido"}, status=405)
     
    try:
        usuario = Usuario.objects.get(id=id)
        return render(request, 'app_gestion_centro_cultural/usuarios/info_usuario.html', {'usuario': usuario})
    except Usuario.DoesNotExist:
        return render(request, 'app_gestion_centro_cultural/usuarios/info_usuario.html', {'usuario': None})
    
# Editar usuario
def editar_usuario_id(request, id):
    #Comprobamos si existe el usuario con el id recibido
    try:
        usuario = Usuario.objects.get(id=id)
    except Usuario.DoesNotExist:
        #Si no existe mostramos una página con el mensaje de error pertinente
        return render(request, 'app_gestion_centro_cultural/usuarios/info_usuario.html', {'usuario': None})
    
    #Si el usuario existe, comprobamos si se ha eniviado la info o si se esta accediendo al formulario para rellenar
    if request.method == 'POST':
        # Como en este caso estamos editamdo hacemos uso de instance: objeto del modelo que queremos editar.
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('listar_usuarios')
    else:
        form = UsuarioForm(instance=usuario)
        return render(request, 'app_gestion_centro_cultural/shared/formulario_registro.html', {'titulo': 'Editar usuario', 'form': form})
    
# Confirmar eliminar usuario
#
# Este método tiene el siguiente flujo:
# 1. Si el usuario con el id recibido no existe, se muestra una página con el mensaje de error pertinente
# 2. Si el usuario existe y la petición NO ES de tipo POST, se redirige a la página de información del usuario, desde la cual se podrá borrar al usuario 
#    (Para que no se pueda acceder a la acción directamente desde la URL sin pasar por la navegación normal de la página)
#    ANOTACION: En un futuro se podria implementar un guard en esta pagina para evitar que se pueda acceder a ella sin estar autenticado y autorizado.
#               Sin embargo, como este sistema solo se desplegará en local para ser usado por el administrador del centro cultural, no se ha implementado ningún sistema de autenticación ni autorización.
#
# 3. Si el usuario existe y la petición ES de tipo POST, se comprueba si la petición es para confirmar la eliminación del usuario, en cuyo caso se elimina el usuario y se redirige al listado de usuarios
#     En caso de que no sea una petición de confirmacion se renderiza la página de confirmación de eliminación del usuario, 
#     En la pagina de confirmación de eliminación del usuario se hace referencia al referer para poder volver a la página anterior en caso de que el usuario cancele la acción, con fallback a la página de información del usuario
def confirmar_eliminar_usuario(request, id):
    try:
        usuario = Usuario.objects.get(id=id)
    except Usuario.DoesNotExist:
        return render(request, 'app_gestion_centro_cultural/usuarios/info_usuario.html', {'usuario': None})
    
    if request.method == 'POST':
        referer = request.META.get('HTTP_REFERER', reverse('filtrar_usuario', args=[id]))

        if 'confirmar' in request.POST:
            usuario.delete()
            return redirect('listar_usuarios')
        else:
            usuario = Usuario.objects.get(id=id)
            return render(request, 'app_gestion_centro_cultural/usuarios/confirmar_eliminar_usuario.html', {'usuario': usuario, 'referer': referer})
    
    return redirect('filtrar_usuario', id=id)
