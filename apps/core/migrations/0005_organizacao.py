"""
apps.core.migrations.0005_organizacao
========================================
Migration que cria a tabela ``core_organizacao`` com todos os campos
do modelo :class:`~apps.core.models.organizacoes_models.Organizacao`.

Notas
-----
- Requer Python >= 3.12
- Criado por `Welder60 <https://github.com/welder60>`_ em 02 junho 2026
"""

# pylint: disable=invalid-name

import uuid

from django.db import migrations, models

__version__ = "0.0.1"
__license__ = "AGPL V3"


class Migration(migrations.Migration):
    """Migration que cria o modelo Organizacao no banco de dados."""

    dependencies = [
        ("core", "0004_espacofisico"),
    ]

    operations = [
        migrations.CreateModel(
            name="Organizacao",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "nome",
                    models.CharField(
                        max_length=150,
                        verbose_name="Nome da Organização",
                    ),
                ),
                (
                    "descricao",
                    models.TextField(verbose_name="Descrição"),
                ),
                (
                    "foto",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="organizacoes/",
                        verbose_name="Foto da Organização",
                    ),
                ),
            ],
            options={
                "verbose_name": "Organização",
                "verbose_name_plural": "Organizações",
                "ordering": ["nome"],
            },
        ),
    ]
