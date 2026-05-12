# Generated manually because Django is not available in this environment.

import datetime
from django.db import migrations, models


def normalize_existing_activity_days(apps, schema_editor):
    Actividad = apps.get_model("app_gestion_centro_cultural", "Actividad")
    Actividad.objects.update(horario="LUNES")


def normalize_existing_monitor_specializations(apps, schema_editor):
    Monitor = apps.get_model("app_gestion_centro_cultural", "Monitor")
    values = {
        "danza": "DANZA",
        "teatro": "TEATRO",
        "musica": "MUSICA",
        "música": "MUSICA",
        "pintura": "PINTURA",
        "otro": "OTRO",
    }
    for monitor in Monitor.objects.all():
        normalized = values.get(str(monitor.especializacion).strip().lower(), "OTRO")
        if monitor.especializacion != normalized:
            monitor.especializacion = normalized
            monitor.save(update_fields=["especializacion"])


class Migration(migrations.Migration):

    dependencies = [
        ("app_gestion_centro_cultural", "0002_alter_usuario_telefono"),
    ]

    operations = [
        migrations.RunPython(normalize_existing_monitor_specializations, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="monitor",
            name="especializacion",
            field=models.CharField(
                choices=[
                    ("DANZA", "Danza"),
                    ("TEATRO", "Teatro"),
                    ("MUSICA", "Música"),
                    ("PINTURA", "Pintura"),
                    ("OTRO", "Otro"),
                ],
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="actividad",
            name="horario",
            field=models.CharField(
                choices=[
                    ("LUNES", "Lunes"),
                    ("MARTES", "Martes"),
                    ("MIERCOLES", "Miércoles"),
                    ("JUEVES", "Jueves"),
                    ("VIERNES", "Viernes"),
                    ("SABADO", "Sábado"),
                    ("DOMINGO", "Domingo"),
                ],
                default="LUNES",
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name="actividad",
            name="hora",
            field=models.TimeField(default=datetime.time(9, 0)),
        ),
        migrations.RunPython(normalize_existing_activity_days, migrations.RunPython.noop),
    ]
