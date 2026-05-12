# Generated manually because Django is not available in this environment.

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app_gestion_centro_cultural", "0004_alter_actividad_hora"),
    ]

    operations = [
        migrations.AlterField(
            model_name="usuario",
            name="telefono",
            field=models.CharField(
                max_length=20,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        message="El teléfono debe tener el formato '+num xxx xxx xxx' o 'xxx xxx xxx'.",
                        regex=r"^(\+\d+\s)?\d{3}\s\d{3}\s\d{3}$",
                    )
                ],
            ),
        ),
    ]
