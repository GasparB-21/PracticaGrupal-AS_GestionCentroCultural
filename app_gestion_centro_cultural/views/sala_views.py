from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from ..models import Sala
from ..forms import SalaForm
from ..form_error_adapter import FormErrorAdapter


# Consulta de salas
def listar_salas(request):
    if request.method != "GET":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    salas = Sala.objects.all()

    # Filtro por ID
    s_id = request.GET.get('id')
    if s_id and int(s_id) >= 0:
        salas = salas.filter(id__icontains=s_id)

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
        {"titulo": "Página de registro de salas", "form": form, "referer": referer},
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
        {"titulo": "Editar sala", "form": form, "referer": referer},
    )


# Confirmar eliminar sala
def confirmar_eliminar_sala(request, id):
    try:
        sala = Sala.objects.get(id=id)
    except Sala.DoesNotExist:
        return render(
            request, "app_gestion_centro_cultural/salas/info_sala.html", {"sala": None}
        )

    if request.method == "POST":
        referer = request.META.get("HTTP_REFERER", reverse("filtrar_sala", args=[id]))

        if "confirmar" in request.POST:
            sala.delete()
            return redirect("listar_salas")

        return render(
            request,
            "app_gestion_centro_cultural/salas/confirmar_eliminar_sala.html",
            {"sala": sala, "referer": referer},
        )

    return redirect("filtrar_sala", id=id)
