from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from ..models import Monitor
from ..forms import MonitorForm
from ..form_error_adapter import FormErrorAdapter

# Consulta de monitores
def listar_monitores(request):
    if request.method != "GET":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    monitores = Monitor.objects.all()

    # Filtro por ID
    m_id = request.GET.get('id')
    if m_id and int(m_id) >= 0:
        monitores = monitores.filter(id__icontains=m_id)

    return render(request, 'app_gestion_centro_cultural/monitores/lista_monitores.html', {
        'monitores': monitores
    })

# Registrar un nuevo monitor
def formulario_registro_monitor(request):
    referer = request.META.get('HTTP_REFERER', reverse('listar_monitores'))
    force_error = request.GET.get('debug_error') == '1'

    if request.method == 'POST':
        form = MonitorForm(request.POST)
        if force_error:
            form.add_error(None, "Error global forzado (POST)")
            form.add_error('nombre', "Error en nombre (POST)")
        
        if form.is_valid():
            form.save()
            return redirect('listar_monitores')
    else:
        if force_error:
            form = MonitorForm(data={}) 
            form.add_error(None, "Error global forzado desde la vista (GET)")
        else:
            form = MonitorForm()

    # Si hay errores y estamos en modo debug, mandamos a la pantalla de error
    if force_error or (request.method == 'POST' and not form.is_valid()):
        return render(request, 'app_gestion_centro_cultural/shared/error.html', {
            'titulo': 'Error en el Registro de Monitor',
            'error_adapter': FormErrorAdapter(form),
            'referer': referer
        })

    return render(request, 'app_gestion_centro_cultural/shared/formulario_registro.html', {
        'titulo': 'Página de registro de monitores',
        'form': form,
        'referer': referer,
        'error_adapter': FormErrorAdapter(form),
    })

def editar_monitor_id(request, id):
    try:
        monitor = Monitor.objects.get(id=id)
    except Monitor.DoesNotExist:
        return render(request, 'app_gestion_centro_cultural/monitores/info_monitor.html', {'monitor': None})

    referer = request.META.get('HTTP_REFERER', reverse('filtrar_monitor', args=[id]))
    force_error = request.GET.get('debug_error') == '1'

    if request.method == 'POST':
        form = MonitorForm(request.POST, instance=monitor)
        if force_error:
            form.add_error(None, "Error global forzado en edición (POST)")
        
        if form.is_valid():
            form.save()
            return redirect('listar_monitores')
    else:
        if force_error:
            form = MonitorForm(data={}, instance=monitor)
            form.add_error(None, "Error global forzado en edición (GET)")
        else:
            form = MonitorForm(instance=monitor)

    # Si hay errores, mandamos a la pantalla de error
    if force_error or (request.method == 'POST' and not form.is_valid()):
        return render(request, 'app_gestion_centro_cultural/shared/error.html', {
            'titulo': 'Error al Editar Monitor',
            'error_adapter': FormErrorAdapter(form),
            'referer': referer
        })

    return render(request, 'app_gestion_centro_cultural/shared/formulario_registro.html', {
        'titulo': 'Editar monitor',
        'form': form,
        'referer': referer,
        'error_adapter': FormErrorAdapter(form),
    })

# Filtrar monitor por id
def filtrar_monitor_id(request, id):
    if request.method != "GET":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        monitor = Monitor.objects.get(id=id)
    except Monitor.DoesNotExist:
        monitor = None

    return render(request, 'app_gestion_centro_cultural/monitores/info_monitor.html', {
        'monitor': monitor
    })

# Confirmar eliminar monitor
def confirmar_eliminar_monitor(request, id):
    try:
        monitor = Monitor.objects.get(id=id)
    except Monitor.DoesNotExist:
        return render(request, 'app_gestion_centro_cultural/monitores/info_monitor.html', {
            'monitor': None
        })

    referer = request.META.get('HTTP_REFERER', reverse('filtrar_monitor', args=[id]))

    if request.method == 'POST':
        if 'confirmar' in request.POST:
            monitor.delete()
            return redirect('listar_monitores')

        return render(request, 'app_gestion_centro_cultural/monitores/confirmar_eliminar_monitor.html', {
            'monitor': monitor,
            'referer': referer
        })

    return redirect('filtrar_monitor', id=id)
