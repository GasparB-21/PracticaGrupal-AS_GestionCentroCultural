from django import forms
from .models import Usuario, Monitor, Sala, Actividad, Inscripcion

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = '__all__'

class MonitorForm(forms.ModelForm):
    class Meta:
        model = Monitor
        fields = '__all__'


class SalaForm(forms.ModelForm):
    class Meta:
        model = Sala
        fields = '__all__'


class ActividadForm(forms.ModelForm):
    class Meta:
        model = Actividad
        fields = '__all__'
        widgets = {
            # Esto convierte el input de texto en un selector de fecha y hora real
            'horario': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class InscripcionForm(forms.ModelForm):
    class Meta:
        model = Inscripcion
        fields = ['usuario']