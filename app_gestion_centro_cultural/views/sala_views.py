from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from ..models import Sala
from ..forms import SalaForm
from ..form_error_adapter import FormErrorAdapter
from django.db.models import ProtectedError

# Consulta de salas
def listar_salas(request):
    if request.method != "GET":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    salas = Sala.objects.all()

    # Filtro por ID
    s_id = request.GET.get('id')
    if s_id:
        s_id = s_id.strip()
        if s_id.isdigit():
            salas = salas.filter(id=int(s_id))
        else:
            salas = salas.none()

    return render(
        request,
        "app_gestion_centro_cultural/salas/lista_salas.html",
        {"salas": salas},
    )


# Registrar una nueva sala
def formulario_registro_sala(request):
    referer = request.META.get("HTTP_REFERER", reverse("listar_salas"))

    if request.method == "POST":
        form = SalaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("listar_salas")
        return render(
            request,
            "app_gestion_centro_cultural/shared/formulario_registro.html",
            {"titulo": "Registrar una sala", "form": form, "referer": referer, "back_label": "Volver al listado de salas", "error_adapter": FormErrorAdapter(form)},
        )

    form = SalaForm()
    return render(
        request,
        "app_gestion_centro_cultural/shared/formulario_registro.html",
        {"titulo": "Registrar una sala", "form": form, "referer": referer, "back_label": "Volver al listado de salas", "error_adapter": FormErrorAdapter(form)},
    )


# Filtrar sala por id
def filtrar_sala_id(request, id):
    if request.method != "GET":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        sala = Sala.objects.get(id=id)
        return render(
            request, "app_gestion_centro_cultural/salas/info_sala.html", {"sala": sala}
        )
    except Sala.DoesNotExist:
        return render(
            request, "app_gestion_centro_cultural/salas/info_sala.html", {"sala": None}
        )


# Editar sala
def _get_safe_next_url(request):
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return None


def editar_sala_id(request, id):
    try:
        sala = Sala.objects.get(id=id)
    except Sala.DoesNotExist:
        return render(
            request, "app_gestion_centro_cultural/salas/info_sala.html", {"sala": None}
        )

    next_url = _get_safe_next_url(request)
    referer = next_url or request.META.get("HTTP_REFERER", reverse("filtrar_sala", args=[id]))
    back_label = "Volver a la eliminación del monitor" if next_url else "Volver al detalle de la sala"

    if request.method == "POST":
        form = SalaForm(request.POST, instance=sala)
        if form.is_valid():
            form.save()
            if next_url:
                return redirect(next_url)
            return redirect("listar_salas")
        return render(
            request,
            "app_gestion_centro_cultural/shared/formulario_registro.html",
            {"titulo": "Editar sala", "form": form, "referer": referer, "back_label": back_label, "error_adapter": FormErrorAdapter(form), "next_url": next_url},
        )

    form = SalaForm(instance=sala)
    return render(
        request,
        "app_gestion_centro_cultural/shared/formulario_registro.html",
        {"titulo": "Editar sala", "form": form, "referer": referer, "back_label": back_label, "error_adapter": FormErrorAdapter(form), "next_url": next_url},
    )


# Confirmar eliminar sala
def _render_confirmar_eliminar_sala(request, sala, referer):
    return render(
        request,
        "app_gestion_centro_cultural/salas/confirmar_eliminar_sala.html",
        {
            "sala": sala,
            "referer": referer,
            "actividades_bloqueantes": sala.actividades_como_sala_principal.order_by("nombre"),
        },
    )


def confirmar_eliminar_sala(request, id):
    try:
        sala = Sala.objects.get(id=id)
    except Sala.DoesNotExist:
        return render(
            request, "app_gestion_centro_cultural/salas/info_sala.html", {"sala": None}
        )

    referer = request.META.get("HTTP_REFERER", reverse("filtrar_sala", args=[id]))
    actividades_bloqueantes = sala.actividades_como_sala_principal.order_by("nombre")
    
    if request.method == "POST":
        if "confirmar" in request.POST:
            if actividades_bloqueantes.exists():
                return _render_confirmar_eliminar_sala(request, sala, referer)

            try:
                sala.delete()
                return redirect("listar_salas")
            except ProtectedError:
                return _render_confirmar_eliminar_sala(request, sala, referer)
        
        return _render_confirmar_eliminar_sala(request, sala, referer)

    return _render_confirmar_eliminar_sala(request, sala, reverse("filtrar_sala", args=[id]))
