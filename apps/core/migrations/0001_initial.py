"""
apps.core.migrations.0001_initial
===================================
Migration inicial do domínio de Eventos.

Cria a tabela ``core_evento`` com todos os campos do modelo
:class:`~apps.core.models.eventos_models.Evento`.

Notas
-----
- Requer Python >= 3.12
- Criado por `Gui-fga <https://github.com/Gui-fga>`_ em 30 maio 2026
- Revisado por `Saresu <https://github.com/Saresu>`_ em 30 maio 2026
- Alterado por `Welder60 <https://github.com/welder60>`_ em 02 junho 2026
"""

# pylint: disable=invalid-name

import uuid

from django.db import migrations, models


__version__ = "0.0.2"
__license__ = "AGPL V3"


class Migration(migrations.Migration):
    """Migration inicial que cria o modelo Evento no banco de dados."""

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Evento",
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
                    models.CharField(max_length=100, verbose_name="Nome do Evento"),
                ),
                ("data", models.DateField(verbose_name="Data do Evento")),
                ("horario", models.TimeField(verbose_name="Horario do Evento")),
                ("local", models.CharField(max_length=150, verbose_name="Local")),
                (
                    "organizador",
                    models.CharField(max_length=100, verbose_name="Organizador"),
                ),
                ("gestor", models.CharField(max_length=100, verbose_name="Gestor")),
                (
                    "descricao",
                    models.TextField(blank=True, null=True, verbose_name="Descricao"),
                ),
                (
                    "capacidade",
                    models.PositiveIntegerField(verbose_name="Capacidade de Pessoas"),
                ),
                (
                    "imagem",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="eventos/",
                        verbose_name="Imagem do Evento",
                    ),
                ),
                (
                    "criado_em",
                    models.DateTimeField(auto_now_add=True, verbose_name="Criado em"),
                ),
                (
                    "atualizado_em",
                    models.DateTimeField(auto_now=True, verbose_name="Atualizado em"),
                ),
            ],
            options={
                "verbose_name": "Evento",
                "verbose_name_plural": "Eventos",
                "ordering": ["-data", "-horario"],
            },
        ),
    ]
