"""
apps.core.migrations.0005_alter_evento_id_uuid
================================================
Altera o campo ``id`` do model :class:`~apps.core.models.eventos_models.Evento`
de ``BigAutoField`` para ``UUIDField``.

Notas
-----
- Requer Python >= 3.12
"""

import uuid

from django.db import migrations, models


__version__ = "0.0.1"
__license__ = "AGPL V3"


class Migration(migrations.Migration):
    """Migra o PK de Evento de BigAutoField para UUIDField."""

    dependencies = [
        ("core", "0004_espacofisico"),
    ]

    operations = [
        migrations.AlterField(
            model_name="evento",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4,
                editable=False,
                primary_key=True,
                serialize=False,
                verbose_name="ID",
            ),
        ),
    ]
