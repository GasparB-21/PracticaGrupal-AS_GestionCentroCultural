from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from .forms import ActividadForm
from .models import Actividad, DiaSemana, Inscripcion, Monitor, Sala, TipoActividad, Usuario


class ReglasDominioTests(TestCase):
    def crear_monitor(self, nombre="Monitor"):
        return Monitor.objects.create(nombre=nombre, especializacion=TipoActividad.MUSICA)

    def crear_sala(self, nombre="Sala", responsable=None):
        return Sala.objects.create(
            nombre=nombre,
            capacidad=20,
            ubicacion="Planta 1",
            responsable=responsable,
        )

    def crear_actividad(self, nombre, sala_principal, monitor=None, plazas=2, hora="08:00"):
        if monitor is None:
            monitor = self.crear_monitor(f"Monitor {nombre}")

        return Actividad.objects.create(
            nombre=nombre,
            tipo=TipoActividad.MUSICA,
            horario=DiaSemana.LUNES,
            hora=hora,
            descripcion="Actividad de prueba",
            duracion=60,
            plazas_disponibles=plazas,
            monitor=monitor,
            sala_principal=sala_principal,
        )

    def crear_usuario(self, nombre, email, telefono):
        return Usuario.objects.create(
            nombre=nombre,
            edad=25,
            email=email,
            telefono=telefono,
        )

    def test_inscripcion_actualiza_plazas_y_bloquea_si_no_quedan(self):
        actividad = self.crear_actividad("Guitarra", self.crear_sala(), plazas=1)
        usuario = self.crear_usuario("Ana", "ana@example.com", "600 000 001")
        otro_usuario = self.crear_usuario("Luis", "luis@example.com", "600 000 002")

        Inscripcion.objects.create(actividad=actividad, usuario=usuario)
        actividad.refresh_from_db()

        self.assertEqual(actividad.plazas_disponibles, 0)

        with self.assertRaises(ValidationError):
            Inscripcion.objects.create(actividad=actividad, usuario=otro_usuario)

        Inscripcion.objects.get(actividad=actividad, usuario=usuario).delete()
        actividad.refresh_from_db()

        self.assertEqual(actividad.plazas_disponibles, 1)

    def test_actividad_no_puede_repetir_sala_principal_como_secundaria(self):
        sala = self.crear_sala()
        actividad = self.crear_actividad("Piano", sala)

        with self.assertRaises(ValidationError):
            actividad.salas_secundarias.add(sala)

    def test_no_se_permite_solapar_una_sala_en_mismo_dia_y_hora(self):
        sala_compartida = self.crear_sala("Sala compartida")
        self.crear_actividad("Teatro", sala_compartida)

        with self.assertRaises(ValidationError):
            self.crear_actividad("Danza", sala_compartida)

    def test_no_se_permite_solapar_sala_secundaria_en_mismo_dia_y_hora(self):
        sala_compartida = self.crear_sala("Sala compartida")
        self.crear_actividad("Teatro", sala_compartida)
        actividad = self.crear_actividad("Danza", self.crear_sala("Sala principal 2"))

        with self.assertRaises(ValidationError):
            actividad.salas_secundarias.add(sala_compartida)

    def test_formulario_actividad_obliga_a_elegir_tipo_y_dia(self):
        form = ActividadForm(data={
            "nombre": "Actividad sin tipo ni dia",
            "tipo": "",
            "horario": "",
            "hora": "08:00",
            "descripcion": "Actividad de prueba",
            "duracion": 60,
            "plazas_disponibles": 5,
            "monitor": self.crear_monitor().id,
            "sala_principal": self.crear_sala().id,
            "salas_secundarias": [],
        })

        self.assertFalse(form.is_valid())
        self.assertIn("tipo", form.errors)
        self.assertIn("horario", form.errors)
    

    # Se pueden agregar más tests para cubrir otras reglas de negocio, como validaciones de email, teléfono, etc.
    def test_usuario_puede_inscribirse_en_varias_actividades(self):
        usuario = self.crear_usuario("Ana", "ana2@example.com", "600 000 003")
        actividad1 = self.crear_actividad("Guitarra", self.crear_sala("Sala A"), plazas=3, hora="08:00")
        actividad2 = self.crear_actividad("Piano", self.crear_sala("Sala B"), plazas=3, hora="09:00")

        Inscripcion.objects.create(actividad=actividad1, usuario=usuario)
        Inscripcion.objects.create(actividad=actividad2, usuario=usuario)

        self.assertEqual(usuario.actividades.count(), 2)

    def test_actividad_puede_tener_varios_usuarios_inscritos(self):
        actividad = self.crear_actividad("Coro", self.crear_sala("Sala C"), plazas=3)
        usuario1 = self.crear_usuario("Ana", "ana3@example.com", "600 000 004")
        usuario2 = self.crear_usuario("Luis", "luis2@example.com", "600 000 005")

        Inscripcion.objects.create(actividad=actividad, usuario=usuario1)
        Inscripcion.objects.create(actividad=actividad, usuario=usuario2)

        self.assertEqual(actividad.usuarios.count(), 2)

    def test_usuario_no_puede_inscribirse_dos_veces_en_misma_actividad(self):
        actividad = self.crear_actividad("Teatro", self.crear_sala("Sala D"), plazas=3)
        usuario = self.crear_usuario("Ana", "ana4@example.com", "600 000 006")

        Inscripcion.objects.create(actividad=actividad, usuario=usuario)

        with self.assertRaises((IntegrityError, ValidationError)):
            with transaction.atomic():
                Inscripcion.objects.create(actividad=actividad, usuario=usuario)

    def test_monitor_puede_tener_varias_actividades_asignadas(self):
        monitor = self.crear_monitor("Monitor común")

        self.crear_actividad("Actividad 1", self.crear_sala("Sala E"), monitor=monitor, hora="08:00")
        self.crear_actividad("Actividad 2", self.crear_sala("Sala F"), monitor=monitor, hora="09:00")

        self.assertEqual(monitor.actividades.count(), 2)
        self.assertEqual(monitor.numero_actividades_asignadas, 2)

    def test_actividad_no_puede_crearse_sin_monitor(self):
        sala = self.crear_sala("Sala G")

        with self.assertRaises(ValidationError):
            Actividad.objects.create(
                nombre="Actividad sin monitor",
                tipo=TipoActividad.MUSICA,
                horario=DiaSemana.LUNES,
                hora="08:00",
                descripcion="Actividad de prueba",
                duracion=60,
                plazas_disponibles=5,
                sala_principal=sala,
            )

    def test_actividad_no_puede_crearse_sin_sala_principal(self):
        monitor = self.crear_monitor("Monitor sin sala")

        with self.assertRaises(ValidationError):
            Actividad.objects.create(
                nombre="Actividad sin sala principal",
                tipo=TipoActividad.MUSICA,
                horario=DiaSemana.LUNES,
                hora="08:00",
                descripcion="Actividad de prueba",
                duracion=60,
                plazas_disponibles=5,
                monitor=monitor,
            )

    def test_sala_puede_no_tener_responsable(self):
        sala = self.crear_sala("Sala sin responsable")

        self.assertIsNone(sala.responsable)

    def test_monitor_no_puede_ser_responsable_de_mas_de_una_sala(self):
        monitor = self.crear_monitor("Monitor responsable")

        self.crear_sala("Sala H", responsable=monitor)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.crear_sala("Sala I", responsable=monitor)

    def test_email_de_usuario_debe_ser_unico(self):
        self.crear_usuario("Ana", "repetido@example.com", "600 000 007")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.crear_usuario("Luis", "repetido@example.com", "600 000 008")

    def test_telefono_de_usuario_debe_ser_unico(self):
        self.crear_usuario("Ana", "ana5@example.com", "600 000 009")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.crear_usuario("Luis", "luis5@example.com", "600 000 009")

    def test_nombre_de_sala_debe_ser_unico(self):
        self.crear_sala("Sala repetida")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.crear_sala("Sala repetida")
