from django.contrib import admin
from .models import Usuario, Monitor, Sala, Actividad, Inscripcion, ActividadSalaSecundaria

# Register your models here.
admin.site.register(Usuario)
admin.site.register(Monitor)
admin.site.register(Sala)
admin.site.register(Actividad)
admin.site.register(Inscripcion)
admin.site.register(ActividadSalaSecundaria)