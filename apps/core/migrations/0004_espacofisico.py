"""
apps.core.migrations.0004_espacofisico
========================================
Migration que cria a tabela ``core_espacofisico`` com todos os campos
do modelo :class:`~apps.core.models.espacos_models.EspacoFisico`.

Notas
-----
- Requer Python >= 3.12
- Criado por `Welder60 <https://github.com/welder60>`_ em 01 abril 2026
"""

# pylint: disable=invalid-name

import uuid

from django.db import migrations, models

__version__ = "0.0.1"
__license__ = "AGPL V3"


class Migration(migrations.Migration):
    """Migration que cria o modelo EspacoFisico no banco de dados."""

    dependencies = [
        ("core", "0003_alter_evento_descricao_alter_evento_horario_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="EspacoFisico",
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
                    models.CharField(max_length=150, verbose_name="Nome do Espaço"),
                ),
                (
                    "foto",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="espacos/",
                        verbose_name="Foto do Espaço",
                    ),
                ),
                (
                    "localizacao",
                    models.TextField(verbose_name="Localização"),
                ),
                (
                    "descricao",
                    models.TextField(verbose_name="Descrição"),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("disponivel", "Disponível"),
                            ("em_manutencao", "Em Manutenção"),
                            ("desativado", "Desativado"),
                        ],
                        default="disponivel",
                        max_length=20,
                        verbose_name="Status",
                    ),
                ),
                (
                    "criado_em",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Criado em"
                    ),
                ),
                (
                    "atualizado_em",
                    models.DateTimeField(auto_now=True, verbose_name="Atualizado em"),
                ),
            ],
            options={
                "verbose_name": "Espaço Físico",
                "verbose_name_plural": "Espaços Físicos",
                "ordering": ["nome"],
            },
        ),
    ]
