from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from ..models import Monitor
from ..forms import MonitorForm

# Consulta de monitores
def listar_monitores(request):
    if request.method != "GET":
        return JsonResponse({"error": "Método no permitido"}, status=405)
    
    listar_monitores = Monitor.objects.all()
    dirMonitores = {'monitores': listar_monitores}
    return render(request, 'app_gestion_centro_cultural/monitores/lista_monitores.html', dirMonitores)

# Registrar un nuevo monitor
def formulario_registro_monitor(request):
    referer = request.META.get('HTTP_REFERER', reverse('listar_monitores'))

    #Comprobamos si se esta accediendo al formulario o si ya se ha mandado con la información
    if request.method == 'POST':
        #Creamos un form con los datos recibidos
        form = MonitorForm(request.POST)
        #Validamos los datos recibidos
        if form.is_valid():
            form.save()
            return redirect('listar_monitores')
        return render(request, 'app_gestion_centro_cultural/shared/formulario_registro.html', {'titulo': 'Página de registro de monitores', 'form': form, 'referer': referer})
    else:
        form = MonitorForm()
        return render(request, 'app_gestion_centro_cultural/shared/formulario_registro.html', {'titulo': 'Página de registro de monitores', 'form': form, 'referer': referer})

# Filtrar monitor por id
def filtrar_monitor_id(request, id):
    if request.method != "GET":
        return JsonResponse({"error": "Método no permitido"}, status=405)
     
    try:
        monitor = Monitor.objects.get(id=id)
        return render(request, 'app_gestion_centro_cultural/monitores/info_monitor.html', {'monitor': monitor})
    except Monitor.DoesNotExist:
        return render(request, 'app_gestion_centro_cultural/monitores/info_monitor.html', {'monitor': None})
    
# Editar monitor
def editar_monitor_id(request, id):
    #Comprobamos si existe el monitor con el id recibido
    try:
        monitor = Monitor.objects.get(id=id)
    except Monitor.DoesNotExist:
        #Si no existe mostramos una página con el mensaje de error pertinente
        return render(request, 'app_gestion_centro_cultural/monitores/info_monitor.html', {'monitor': None})
    
    referer = request.META.get('HTTP_REFERER', reverse('filtrar_monitor', args=[id]))

    #Si el monitor existe, comprobamos si se ha enviado la info o si se esta accediendo al formulario para rellenar
    if request.method == 'POST':
        # Como en este caso estamos editando hacemos uso de instance: objeto del modelo que queremos editar.
        form = MonitorForm(request.POST, instance=monitor)
        if form.is_valid():
            form.save()
            return redirect('listar_monitores')
        return render(request, 'app_gestion_centro_cultural/shared/formulario_registro.html', {'titulo': 'Editar monitor', 'form': form, 'referer': referer})
    else:
        form = MonitorForm(instance=monitor)
        return render(request, 'app_gestion_centro_cultural/shared/formulario_registro.html', {'titulo': 'Editar monitor', 'form': form, 'referer': referer})
    
# Confirmar eliminar monitor
def confirmar_eliminar_monitor(request, id):
    try:
        monitor = Monitor.objects.get(id=id)
    except Monitor.DoesNotExist:
        return render(request, 'app_gestion_centro_cultural/monitores/info_monitor.html', {'monitor': None})
    
    if request.method == 'POST':
        referer = request.META.get('HTTP_REFERER', reverse('filtrar_monitor', args=[id]))

        if 'confirmar' in request.POST:
            monitor.delete()
            return redirect('listar_monitores')
        else:
            return render(request, 'app_gestion_centro_cultural/monitores/confirmar_eliminar_monitor.html', {'monitor': monitor, 'referer': referer})
    
    return redirect('filtrar_monitor', id=id)
