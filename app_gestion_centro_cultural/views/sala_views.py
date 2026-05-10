from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from ..models import Sala
from ..forms import SalaForm
from ..form_error_adapter import FormErrorAdapter
from django.contrib import messages
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
            {"titulo": "Página de registro de salas", "form": form, "referer": referer, "error_adapter": FormErrorAdapter(form)},
        )

    form = SalaForm()
    return render(
        request,
        "app_gestion_centro_cultural/shared/formulario_registro.html",
        {"titulo": "Página de registro de salas", "form": form, "referer": referer, "error_adapter": FormErrorAdapter(form)},
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
def editar_sala_id(request, id):
    try:
        sala = Sala.objects.get(id=id)
    except Sala.DoesNotExist:
        return render(
            request, "app_gestion_centro_cultural/salas/info_sala.html", {"sala": None}
        )

    referer = request.META.get("HTTP_REFERER", reverse("filtrar_sala", args=[id]))

    if request.method == "POST":
        form = SalaForm(request.POST, instance=sala)
        if form.is_valid():
            form.save()
            return redirect("listar_salas")
        return render(
            request,
            "app_gestion_centro_cultural/shared/formulario_registro.html",
            {"titulo": "Editar sala", "form": form, "referer": referer, "error_adapter": FormErrorAdapter(form)},
        )

    form = SalaForm(instance=sala)
    return render(
        request,
        "app_gestion_centro_cultural/shared/formulario_registro.html",
        {"titulo": "Editar sala", "form": form, "referer": referer, "error_adapter": FormErrorAdapter(form)},
    )


# Confirmar eliminar sala
def confirmar_eliminar_sala(request, id):
    try:
        sala = Sala.objects.get(id=id)
    except Sala.DoesNotExist:
        return render(
            request, "app_gestion_centro_cultural/salas/info_sala.html", {"sala": None}
        )

    actividades_bloqueantes = sala.actividades_como_sala_principal.all()
    referer = request.META.get("HTTP_REFERER", reverse("filtrar_sala", args=[id]))
    
    if request.method == "POST":
        if "confirmar" in request.POST:
            try:
                sala.delete()
                return redirect("listar_salas")
            except ProtectedError:
                messages.error(request, f"No se puede eliminar la sala '{sala.nombre}' porque tiene actividades asignadas.")
            return redirect("listar_salas")
        
        return render(
            request,
            "app_gestion_centro_cultural/salas/confirmar_eliminar_sala.html",
            {
                "sala": sala, 
                "referer": referer,
                "actividades_bloqueantes": actividades_bloqueantes
            },
        )
    return redirect("filtrar_sala", id=id)
