"""
apps.core.migrations.0005_evento_status
========================================
Adiciona o campo ``status`` ao model
:class:`~apps.core.models.eventos_models.Evento`.

Valores possíveis: ``rascunho`` (padrão) e ``publicado``.

Notas
-----
- Requer Python >= 3.12
- Criado por `Welder60 <https://github.com/welder60>`_ em 02 junho 2026
"""

from django.db import migrations, models


__version__ = "0.0.1"
__license__ = "AGPL V3"


class Migration(migrations.Migration):
    """Adiciona campo status (Rascunho/Publicado) ao model Evento."""

    dependencies = [
        ("core", "0004_espacofisico"),
    ]

    operations = [
        migrations.AddField(
            model_name="evento",
            name="status",
            field=models.CharField(
                choices=[("rascunho", "Rascunho"), ("publicado", "Publicado")],
                default="rascunho",
                max_length=10,
                verbose_name="Status",
            ),
        ),
    ]
