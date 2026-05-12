from django import forms
from .models import Usuario, Monitor, Sala, Actividad, Inscripcion, ActividadSalaSecundaria


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

    def clean_responsable(self):
        responsable = self.cleaned_data.get('responsable')
        if not responsable:
            return responsable

        sala_existente = Sala.objects.filter(responsable=responsable).exclude(pk=self.instance.pk).first()
        if sala_existente:
            raise forms.ValidationError(
                f'La sala "{sala_existente.nombre}" ya tiene a "{responsable.nombre}" como responsable.'
            )

        return responsable


class ActividadForm(SpanishValidationMessagesMixin, forms.ModelForm):
    salas_secundarias = forms.ModelMultipleChoiceField(
        queryset=Sala.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-list'}),
    )
    tipo = forms.ChoiceField(
        choices=[('', '---------')] + list(Actividad._meta.get_field('tipo').choices),
        required=True,
        error_messages={'required': 'Selecciona un tipo de actividad.'},
    )
    horario = forms.ChoiceField(
        choices=[('', '---------')] + list(Actividad._meta.get_field('horario').choices),
        required=True,
        error_messages={'required': 'Selecciona un día de la semana.'},
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk and not self.is_bound:
            self.fields['tipo'].initial = ''
            self.fields['horario'].initial = ''
            self.fields['hora'].initial = '08:00'

    def _post_clean(self):
        self.instance._skip_model_overlap_validation = True
        try:
            super()._post_clean()
        finally:
            if hasattr(self.instance, '_skip_model_overlap_validation'):
                delattr(self.instance, '_skip_model_overlap_validation')

    def clean(self):
        cleaned_data = super().clean()
        sala_principal = cleaned_data.get('sala_principal')
        salas_secundarias = cleaned_data.get('salas_secundarias')
        horario = cleaned_data.get('horario')
        hora = cleaned_data.get('hora')

        if not sala_principal or not horario or not hora:
            return cleaned_data

        salas_secundarias_ids = set()
        if salas_secundarias:
            salas_secundarias_ids = {sala.id for sala in salas_secundarias}

        if sala_principal.id in salas_secundarias_ids:
            self.add_error(
                'salas_secundarias',
                'Una actividad no puede tener la misma sala como principal y secundaria.',
            )

        actividad_id = self.instance.pk
        salas_a_validar = [sala_principal]
        if salas_secundarias:
            salas_a_validar.extend(salas_secundarias)

        for sala in salas_a_validar:
            actividad_solapada_principal = Actividad.objects.filter(
                horario=horario,
                hora=hora,
                sala_principal=sala,
            ).exclude(pk=actividad_id).exists()

            actividad_solapada_secundaria = ActividadSalaSecundaria.objects.filter(
                sala=sala,
                actividad__horario=horario,
                actividad__hora=hora,
            ).exclude(actividad_id=actividad_id).exists()

            if actividad_solapada_principal or actividad_solapada_secundaria:
                mensaje = f'La sala "{sala.nombre}" ya está asignada a otra actividad en el mismo día y hora.'
                if sala == sala_principal:
                    self.add_error('sala_principal', mensaje)
                else:
                    self.add_error('salas_secundarias', mensaje)

        return cleaned_data


class InscripcionForm(SpanishValidationMessagesMixin, forms.ModelForm):
    def __init__(self, *args, actividad=None, **kwargs):
        super().__init__(*args, **kwargs)
        if actividad:
            self.fields['usuario'].queryset = Usuario.objects.exclude(
                inscripciones__actividad=actividad
            )

    class Meta:
        model = Inscripcion
        fields = ['usuario']
        widgets = {
            'usuario': forms.Select(),
        }
