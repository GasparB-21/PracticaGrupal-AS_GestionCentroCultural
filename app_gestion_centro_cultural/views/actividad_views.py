from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from ..models import Actividad, Usuario
from ..forms import ActividadForm, InscripcionForm


# Consulta de actividades
def listar_actividades(request):
    if request.method != "GET":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    actividades = Actividad.objects.all()
    tipo = request.GET.get("tipo")
    if tipo:
        actividades = actividades.filter(tipo=tipo)
    monitor_id = request.GET.get("monitor")
    if monitor_id:
        actividades = actividades.filter(monitor_id=monitor_id)

    return render(
        request,
        "app_gestion_centro_cultural/actividades/lista_actividades.html",
        {"actividades": actividades},
    )


# Registrar una nueva actividad
def formulario_registro_actividad(request):
    referer = request.META.get("HTTP_REFERER", reverse("listar_actividades"))

    if request.method == "POST":
        form = ActividadForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("listar_actividades")
        return render(
            request,
            "app_gestion_centro_cultural/shared/formulario_registro.html",
            {"titulo": "Página de registro de actividades", "form": form, "referer": referer},
        )

    form = ActividadForm()
    return render(
        request,
        "app_gestion_centro_cultural/shared/formulario_registro.html",
        {"titulo": "Página de registro de actividades", "form": form, "referer": referer},
    )


# Filtrar actividad por id
def filtrar_actividad_id(request, id):
    if request.method != "GET":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        actividad = Actividad.objects.get(id=id)
        return render(
            request,
            "app_gestion_centro_cultural/actividades/info_actividad.html",
            {"actividad": actividad},
        )
    except Actividad.DoesNotExist:
        return render(
            request,
            "app_gestion_centro_cultural/actividades/info_actividad.html",
            {"actividad": None},
        )


# Editar actividad
def editar_actividad_id(request, id):
    try:
        actividad = Actividad.objects.get(id=id)
    except Actividad.DoesNotExist:
        return render(
            request,
            "app_gestion_centro_cultural/actividades/info_actividad.html",
            {"actividad": None},
        )

    referer = request.META.get("HTTP_REFERER", reverse("filtrar_actividad", args=[id]))

    if request.method == "POST":
        form = ActividadForm(request.POST, instance=actividad)
        if form.is_valid():
            form.save()
            return redirect("listar_actividades")
        return render(
            request,
            "app_gestion_centro_cultural/shared/formulario_registro.html",
            {"titulo": "Editar actividad", "form": form, "referer": referer},
        )

    form = ActividadForm(instance=actividad)
    return render(
        request,
        "app_gestion_centro_cultural/shared/formulario_registro.html",
        {"titulo": "Editar actividad", "form": form, "referer": referer},
    )


# Confirmar eliminar actividad
def confirmar_eliminar_actividad(request, id):
    try:
        actividad = Actividad.objects.get(id=id)
    except Actividad.DoesNotExist:
        return render(
            request,
            "app_gestion_centro_cultural/actividades/info_actividad.html",
            {"actividad": None},
        )

    if request.method == "POST":
        referer = request.META.get("HTTP_REFERER", reverse("filtrar_actividad", args=[id]))

        if "confirmar" in request.POST:
            actividad.delete()
            return redirect("listar_actividades")

        return render(
            request,
            "app_gestion_centro_cultural/actividades/confirmar_eliminar_actividad.html",
            {"actividad": actividad, "referer": referer},
        )

    return redirect("filtrar_actividad", id=id)

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
        "app_gestion_centro_cultural/actividades/lista_inscripciones.html",
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
