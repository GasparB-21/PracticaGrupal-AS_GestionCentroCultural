from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from ..models import Actividad
from ..forms import ActividadForm
from ..form_error_adapter import FormErrorAdapter


# Consulta de actividades
def listar_actividades(request):
    if request.method != "GET":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    actividades = Actividad.objects.all()

    # Filtrar por ID
    a_id = request.GET.get('id')
    if a_id:
        a_id = a_id.strip()
        if a_id.isdigit():
            actividades = actividades.filter(id=int(a_id))
        else:
            actividades = actividades.none()

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
            {"titulo": "Registrar una actividad", "form": form, "referer": referer, "back_label": "Volver al listado de actividades", "error_adapter": FormErrorAdapter(form)},
        )

    form = ActividadForm()
    return render(
        request,
        "app_gestion_centro_cultural/shared/formulario_registro.html",
        {"titulo": "Registrar una actividad", "form": form, "referer": referer, "back_label": "Volver al listado de actividades", "error_adapter": FormErrorAdapter(form)},
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
def _get_safe_next_url(request):
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return None


def editar_actividad_id(request, id):
    try:
        actividad = Actividad.objects.get(id=id)
    except Actividad.DoesNotExist:
        return render(
            request,
            "app_gestion_centro_cultural/actividades/info_actividad.html",
            {"actividad": None},
        )

    next_url = _get_safe_next_url(request)
    referer = next_url or request.META.get("HTTP_REFERER", reverse("filtrar_actividad", args=[id]))
    back_label = "Volver a la eliminación del monitor" if next_url else "Volver al detalle de la actividad"

    if request.method == "POST":
        form = ActividadForm(request.POST, instance=actividad)
        if form.is_valid():
            form.save()
            if next_url:
                return redirect(next_url)
            return redirect("listar_actividades")
        return render(
            request,
            "app_gestion_centro_cultural/shared/formulario_registro.html",
            {"titulo": "Editar actividad", "form": form, "referer": referer, "back_label": back_label, "error_adapter": FormErrorAdapter(form), "next_url": next_url},
        )

    form = ActividadForm(instance=actividad)
    return render(
        request,
        "app_gestion_centro_cultural/shared/formulario_registro.html",
        {"titulo": "Editar actividad", "form": form, "referer": referer, "back_label": back_label, "error_adapter": FormErrorAdapter(form), "next_url": next_url},
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
