from django.db import models
from django.core.validators import MaxValueValidator


class Usuario(models.Model):
    nombre = models.CharField(max_length=120)
    edad = models.PositiveIntegerField(validators=[MaxValueValidator(130)])
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20)

    def __str__(self) -> str:
        return self.nombre


class Monitor(models.Model):
    nombre = models.CharField(max_length=120)
    especializacion = models.CharField(max_length=120)

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
    # Definimos los tipos de actividad como una enumeración de texto para garantizar que solo se puedan asignar valores válidos.
    class TipoActividad(models.TextChoices):
        DANZA = "DANZA", "Danza"
        TEATRO = "TEATRO", "Teatro"
        MUSICA = "MUSICA", "Música"
        PINTURA = "PINTURA", "Pintura"
        OTRO = "OTRO", "Otro"

    nombre = models.CharField(max_length=120)
    tipo = models.CharField(
                                max_length=20,
                                choices=TipoActividad.choices,
                                default=TipoActividad.OTRO,
                            )
    horario = models.DateTimeField()
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
                                            # En este no protegemos la relación pq esta es opcional
                                            on_delete=models.SET_NULL,
                                            null=True,
                                            blank=True,
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

    def __str__(self) -> str:
        return f"{self.actividad} -> {self.sala}"

    