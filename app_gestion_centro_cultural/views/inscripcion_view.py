from django.shortcuts import render, redirect
from django.urls import reverse
from ..models import Actividad, Usuario
from ..forms import  InscripcionForm
from ..form_error_adapter import FormErrorAdapter

# Consultar inscripciones de una actividad
def listar_inscripciones(request, id):
    try:
        actividad = Actividad.objects.get(id=id)
        usuarios = actividad.usuarios.all()
    except Actividad.DoesNotExist:
        return render(
            request,
            "app_gestion_centro_cultural/actividades/info_actividad.html",
            {"actividad": None},
        )

    return render(
        request,
        "app_gestion_centro_cultural/inscripciones/lista_inscripciones.html",
        {"actividad": actividad, "usuarios": usuarios},
    )

# Inscribir usuario en actividad
def inscribir_usuario_actividad(request, id):
    try:
        actividad = Actividad.objects.get(id=id)
    except Actividad.DoesNotExist:
        return render(
            request,
            "app_gestion_centro_cultural/actividades/info_actividad.html",
            {"actividad": None},
        )
    referer = reverse("listar_actividades")
    if request.method == "POST":
        form = InscripcionForm(request.POST)
        if form.is_valid():
            usuario = form.cleaned_data['usuario']
            if actividad.usuarios.filter(id=usuario.id).exists():
                form.add_error('usuario', "Este usuario ya está inscrito en esta actividad.")
                return render(
                    request, 
                    "app_gestion_centro_cultural/shared/formulario_registro.html", 
                    {"titulo": f"Inscribir usuario en {actividad.nombre}", "form": form, "referer": referer}
                )
            if actividad.usuarios.count() < actividad.plazas_disponibles:
                nueva_inscripcion = form.save(commit=False)
                nueva_inscripcion.actividad = actividad
                nueva_inscripcion.save()
                return redirect("listar_inscripciones", id=id)
            else:
                form.add_error(None, "No se pueden realizar más inscripciones: No hay plazas disponibles.")
                return render(
                    request, 
                    "app_gestion_centro_cultural/shared/formulario_registro.html", 
                    {"titulo": f"Inscribir usuario en {actividad.nombre}", "form": form, "referer": referer}
                )
    else:
        form = InscripcionForm()
    return render(
        request,
        "app_gestion_centro_cultural/shared/formulario_registro.html",
        {"titulo": f"Inscribir usuario en {actividad.nombre}",
        "form": form, 
        "referer": referer},
    )

# Eliminar inscripcion
def eliminar_inscripcion(request, actividad_id, usuario_id):
    if request.method == "POST":
        try:
            actividad = Actividad.objects.get(id=actividad_id)
            usuario = Usuario.objects.get(id=usuario_id)
            actividad.usuarios.remove(usuario)
        except (Actividad.DoesNotExist, Usuario.DoesNotExist):
            pass
    return redirect("listar_inscripciones", id=actividad_id)
