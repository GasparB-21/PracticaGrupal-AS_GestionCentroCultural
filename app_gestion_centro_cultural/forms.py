from django import forms
from .models import Usuario, Monitor, Sala, Actividad, Inscripcion


SPANISH_FIELD_ERROR_MESSAGES = {
    'required': 'Este campo es obligatorio.',
    'invalid': 'Introduce un valor válido.',
    'invalid_choice': 'Selecciona una opción válida.',
}


class SpanishValidationMessagesMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.error_messages.update(SPANISH_FIELD_ERROR_MESSAGES)


class UsuarioForm(SpanishValidationMessagesMixin, forms.ModelForm):
    class Meta:
        model = Usuario
        fields = '__all__'
        error_messages = {
            'email': {
                'unique': 'Ya existe un usuario con este email.',
                'invalid': 'Introduce un email válido.',
            },
            'telefono': {
                'unique': 'Ya existe un usuario con este teléfono.',
            },
            'edad': {
                'max_value': 'La edad no puede ser superior a 130.',
            },
        }


class MonitorForm(SpanishValidationMessagesMixin, forms.ModelForm):
    class Meta:
        model = Monitor
        fields = '__all__'


class SalaForm(SpanishValidationMessagesMixin, forms.ModelForm):
    class Meta:
        model = Sala
        fields = '__all__'
        error_messages = {
            'nombre': {
                'unique': 'Ya existe una sala con este nombre.',
            },
        }


class ActividadForm(SpanishValidationMessagesMixin, forms.ModelForm):
    salas_secundarias = forms.ModelMultipleChoiceField(
        queryset=Sala.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-list'}),
    )

    class Meta:
        model = Actividad
        fields = [
            'nombre',
            'tipo',
            'horario',
            'hora',
            'descripcion',
            'duracion',
            'plazas_disponibles',
            'monitor',
            'sala_principal',
            'salas_secundarias',
        ]
        widgets = {
            'hora': forms.TimeInput(attrs={'type': 'time'}),
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'duracion': forms.NumberInput(attrs={'min': 1, 'step': 1}),
            'plazas_disponibles': forms.NumberInput(attrs={'min': 0, 'step': 1}),
        }
        labels = {
            'horario': 'Día de la semana',
            'hora': 'Hora',
            'duracion': 'Duración',
        }
        error_messages = {
            'hora': {
                'invalid': 'Introduce una hora válida.',
            },
            'duracion': {
                'invalid': 'Introduce una duración válida en minutos.',
            },
            'plazas_disponibles': {
                'invalid': 'Introduce un número válido de plazas.',
            },
        }


class InscripcionForm(SpanishValidationMessagesMixin, forms.ModelForm):
    class Meta:
        model = Inscripcion
        fields = ['usuario']
        widgets = {
            'usuario': forms.Select(),
        }
