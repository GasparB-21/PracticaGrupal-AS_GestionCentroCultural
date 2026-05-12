from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models.signals import m2m_changed, post_delete
from django.dispatch import receiver
from django.core.validators import MaxValueValidator, RegexValidator


telefono_validator = RegexValidator(
    regex=r"^(\+\d+\s)?\d{3}\s\d{3}\s\d{3}$",
    message="El teléfono debe tener el formato '+num xxx xxx xxx' o 'xxx xxx xxx'.",
)


class TipoActividad(models.TextChoices):
    DANZA = "DANZA", "Danza"
    TEATRO = "TEATRO", "Teatro"
    MUSICA = "MUSICA", "Música"
    PINTURA = "PINTURA", "Pintura"
    OTRO = "OTRO", "Otro"


class DiaSemana(models.TextChoices):
    LUNES = "LUNES", "Lunes"
    MARTES = "MARTES", "Martes"
    MIERCOLES = "MIERCOLES", "Miércoles"
    JUEVES = "JUEVES", "Jueves"
    VIERNES = "VIERNES", "Viernes"
    SABADO = "SABADO", "Sábado"
    DOMINGO = "DOMINGO", "Domingo"


class Usuario(models.Model):
    nombre = models.CharField(max_length=120)
    edad = models.PositiveIntegerField(validators=[MaxValueValidator(130)])
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, unique=True, validators=[telefono_validator])

    def __str__(self) -> str:
        return self.nombre


class Monitor(models.Model):
    nombre = models.CharField(max_length=120)
    especializacion = models.CharField(max_length=20, choices=TipoActividad.choices)

    def __str__(self) -> str:
        return self.nombre

    # Definimos el "número de actividades asignadas" como una propiedad calculada, así evitamos tener que hacer la sincronización 
    # manualmente cada vez que se asigna o desasigna una actividad al monitor.
    @property
    def numero_actividades_asignadas(self) -> int:
        return self.actividades.count()


class Sala(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    capacidad = models.PositiveIntegerField()
    ubicacion = models.CharField(max_length=200)
    responsable = models.OneToOneField(
                                            Monitor,
                                            # Sí se elimina el monitor responsable el valor pasa a NULL
                                            on_delete=models.SET_NULL,
                                            # Permite que el campo sea NULL en la base de datos
                                            null=True,
                                            # Permite que el campo sea NULL en los formularios
                                            blank=True,
                                            # Define cómo accedemos a la relación desde el modelo MONITOR
                                            related_name="sala_responsable",
                                        )
                                        
    def __str__(self) -> str:
        return self.nombre


class Actividad(models.Model):
    nombre = models.CharField(max_length=120)
    tipo = models.CharField(
                                max_length=20,
                                choices=TipoActividad.choices,
                                default=TipoActividad.OTRO,
                            )
    horario = models.CharField(max_length=10, choices=DiaSemana.choices, default=DiaSemana.LUNES)
    hora = models.TimeField(default="09:00")
    descripcion = models.TextField()
    # Documentación visible para el usuario en formularios/admin
    duracion = models.PositiveIntegerField(help_text="Duración en minutos")
    plazas_disponibles = models.PositiveIntegerField()

    # Definimos las relaciones con el resto de modelos
    monitor = models.ForeignKey(
                                    Monitor,
                                    # Protegemos la relación, para borrar un monitor primero hay que reasignar o eliminar las 
                                    # actividades que tiene asignadas
                                    on_delete=models.PROTECT,
                                    related_name="actividades",
                                )

    sala_principal = models.ForeignKey(
                                            Sala,
                                            on_delete=models.PROTECT,
                                            related_name="actividades_como_sala_principal",
                                        )

    usuarios = models.ManyToManyField(
                                            Usuario,
                                            through="Inscripcion",
                                            related_name="actividades",
                                            # Una actividad puede existir sin usuarios inscritos
                                            blank=True,
                                        )

    salas_secundarias = models.ManyToManyField(
                                                    Sala,
                                                    through="ActividadSalaSecundaria",
                                                    related_name="actividades_como_sala_secundaria",
                                                    # Una actividad puede no tener salas sacundarias asignadas
                                                    blank=True,
                                                )

    def __str__(self) -> str:
        return self.nombre

    def clean(self):
        super().clean()

        if getattr(self, "_skip_model_overlap_validation", False):
            return

        if not self.sala_principal_id:
            return

        actividades_solapadas = Actividad.objects.filter(
            horario=self.horario,
            hora=self.hora,
        ).exclude(pk=self.pk)

        sala_ocupada_como_principal = actividades_solapadas.filter(
            sala_principal=self.sala_principal
        ).exists()
        sala_ocupada_como_secundaria = actividades_solapadas.filter(
            salas_secundarias=self.sala_principal
        ).exists()

        if sala_ocupada_como_principal or sala_ocupada_como_secundaria:
            raise ValidationError({
                "sala_principal": "Esta sala ya está asignada a otra actividad en el mismo día y hora."
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Inscripcion(models.Model):
    actividad = models.ForeignKey(
                                    Actividad,
                                    on_delete=models.CASCADE,
                                    related_name="inscripciones",
                                )
    usuario = models.ForeignKey(
                                    Usuario,
                                    on_delete=models.CASCADE,
                                    related_name="inscripciones",
                                )
    fecha_inscripcion = models.DateField(auto_now_add=True)

    # Define una restricción de unicidad para evitar que un mismo usuario se inscriba varias veces en la misma actividad.
    class Meta:
        constraints = [ models.UniqueConstraint(
                                                fields=["actividad", "usuario"],
                                                name="unique_inscripcion_actividad_usuario",
                                                )
                        ]

    def clean(self):
        super().clean()

        if not self.actividad_id or not self.usuario_id:
            return

        inscripcion_duplicada = Inscripcion.objects.filter(
            actividad=self.actividad,
            usuario=self.usuario,
        ).exclude(pk=self.pk).exists()

        if inscripcion_duplicada:
            raise ValidationError({
                "usuario": "Este usuario ya está inscrito en esta actividad."
            })

        if self._state.adding and self.actividad.plazas_disponibles <= 0:
            raise ValidationError("No se pueden realizar más inscripciones: no hay plazas disponibles.")

    def save(self, *args, **kwargs):
        if not self._state.adding:
            self.full_clean()
            super().save(*args, **kwargs)
            return

        with transaction.atomic():
            actividad = Actividad.objects.select_for_update().get(pk=self.actividad_id)
            if actividad.plazas_disponibles <= 0:
                raise ValidationError("No se pueden realizar más inscripciones: no hay plazas disponibles.")

            self.actividad = actividad
            self.full_clean()
            super().save(*args, **kwargs)

            Actividad.objects.filter(pk=actividad.pk).update(
                plazas_disponibles=models.F("plazas_disponibles") - 1
            )

    def __str__(self) -> str:
        return f"{self.usuario} -> {self.actividad}"


class ActividadSalaSecundaria(models.Model):
    actividad = models.ForeignKey(
                                    Actividad,
                                    on_delete=models.CASCADE,
                                    related_name="relaciones_salas_secundarias",
                                )
    sala = models.ForeignKey(
                                Sala,
                                on_delete=models.CASCADE,
                                related_name="relaciones_actividades_secundarias",
                            )

    # Define una restricción de unicidad para evitar que una misma sala se asigne varias veces a la misma actividad.
    class Meta:
        constraints = [
                            models.UniqueConstraint(
                                                        fields=["actividad", "sala"],
                                                        name="unique_actividad_sala_secundaria",
                                                    )
                        ]

    def clean(self):
        super().clean()

        if not self.actividad_id or not self.sala_id:
            return

        if self.actividad.sala_principal_id == self.sala_id:
            raise ValidationError({
                "sala": "Una actividad no puede tener la misma sala como principal y secundaria."
            })

        sala_ocupada_como_principal = Actividad.objects.filter(
            horario=self.actividad.horario,
            hora=self.actividad.hora,
            sala_principal=self.sala,
        ).exclude(pk=self.actividad_id).exists()

        sala_ocupada_como_secundaria = ActividadSalaSecundaria.objects.filter(
            sala=self.sala,
            actividad__horario=self.actividad.horario,
            actividad__hora=self.actividad.hora,
        ).exclude(actividad_id=self.actividad_id).exists()

        if sala_ocupada_como_principal or sala_ocupada_como_secundaria:
            raise ValidationError({
                "sala": "Esta sala ya está asignada a otra actividad en el mismo día y hora."
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.actividad} -> {self.sala}"


@receiver(m2m_changed, sender=Actividad.salas_secundarias.through)
def validar_salas_secundarias(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action != "pre_add" or not pk_set:
        return

    if reverse:
        sala = instance
        actividades = Actividad.objects.filter(pk__in=pk_set)
        for actividad in actividades:
            _validar_sala_secundaria(actividad, sala)
        return

    actividad = instance
    salas = Sala.objects.filter(pk__in=pk_set)
    for sala in salas:
        _validar_sala_secundaria(actividad, sala)


def _validar_sala_secundaria(actividad, sala):
    if actividad.sala_principal_id == sala.id:
        raise ValidationError("Una actividad no puede tener la misma sala como principal y secundaria.")

    sala_ocupada_como_principal = Actividad.objects.filter(
        horario=actividad.horario,
        hora=actividad.hora,
        sala_principal=sala,
    ).exclude(pk=actividad.pk).exists()

    sala_ocupada_como_secundaria = ActividadSalaSecundaria.objects.filter(
        sala=sala,
        actividad__horario=actividad.horario,
        actividad__hora=actividad.hora,
    ).exclude(actividad_id=actividad.pk).exists()

    if sala_ocupada_como_principal or sala_ocupada_como_secundaria:
        raise ValidationError("Esta sala ya está asignada a otra actividad en el mismo día y hora.")


@receiver(post_delete, sender=Inscripcion)
def devolver_plaza_disponible(sender, instance, **kwargs):
    Actividad.objects.filter(pk=instance.actividad_id).update(
        plazas_disponibles=models.F("plazas_disponibles") + 1
    )
