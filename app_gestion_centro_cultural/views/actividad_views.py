from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from ..models import Actividad
from ..forms import ActividadForm


# Consulta de actividades
def listar_actividades(request):
    if request.method != "GET":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    actividades = Actividad.objects.all()
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
