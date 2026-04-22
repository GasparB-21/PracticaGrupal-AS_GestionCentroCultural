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
        return render(request, 'app_gestion_centro_cultural/formulario_registro.html', {'titulo': 'Editar usuario', 'form': form})
    
# Confirmar eliminar usuario
def confirmar_eliminar_usuario(request, id):
    try:
        usuario = Usuario.objects.get(id=id)
    except Usuario.DoesNotExist:
        return render(request, 'app_gestion_centro_cultural/usuarios/info_usuario.html', {'usuario': None})
    
    if request.method == 'POST':
        if 'confirmar' in request.POST:
            usuario.delete()
            return redirect('listar_usuarios')
        else:
            # Volver a la página anterior
            referer = request.META.get('HTTP_REFERER', reverse('listar_usuarios'))
            return redirect(referer)
    
    referer = request.META.get('HTTP_REFERER', reverse('listar_usuarios'))
    return render(request, 'app_gestion_centro_cultural/usuarios/confirmar_eliminar_usuario.html', {'usuario': usuario, 'referer': referer})
