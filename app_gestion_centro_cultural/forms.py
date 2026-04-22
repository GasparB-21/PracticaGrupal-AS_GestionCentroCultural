from django import forms
from .models import Usuario, Monitor, Sala, Actividad

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
