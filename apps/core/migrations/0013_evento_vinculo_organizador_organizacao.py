"""Vincula o ``Evento`` a um ``organizador`` (Usuario) e a uma ``organizacao``.

apps.core.migrations.0013_evento_vinculo_organizador_organizacao
=================================================================
Substitui o antigo campo de texto ``organizador`` por uma chave estrangeira
para o usuario organizador e adiciona a chave estrangeira ``organizacao``,
materializando as regras de negocio do dominio de eventos:

- todo evento precisa estar vinculado a um organizador e a uma organizacao;
- somente organizadores vinculados a organizacao podem gerir o evento.

O campo livre ``gestor`` e removido, pois nao faz parte do dominio do evento
(a aprovacao de reservas e responsabilidade do gestor, no dominio de Reservas).

Migracao de dados
-----------------
Para preservar os eventos ja existentes (incluindo os dados de demonstracao),
a antiga string ``organizador`` e convertida em uma ``Organizacao`` de mesmo
nome, e um usuario organizador padrao e criado e vinculado a essa organizacao.

Notas
-----
- Requer Python >= 3.12
- Criado por `Welder60 <https://github.com/welder60>`_ em 23 junho 2026
"""

from __future__ import annotations

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

__version__ = "0.0.1"
__license__ = "AGPL V3"

DESCRICAO_ORG_AUTOMATICA = (
    "Organização criada automaticamente na migração de vínculo de eventos."
)


def converter_eventos(apps, schema_editor):
    """Converte os eventos existentes para o novo vinculo organizador/organizacao."""
    Evento = apps.get_model("core", "Evento")
    Organizacao = apps.get_model("core", "Organizacao")
    Usuario = apps.get_model("security", "Usuario")

    organizador_padrao, _ = Usuario.objects.get_or_create(
        username="organizador_padrao",
        defaults={
            "nome_completo": "Organizador Padrão (migração)",
            "tipo": "OR",
            "is_active": True,
        },
    )

    for evento in list(Evento.objects.all()):
        nome_org = (getattr(evento, "organizador", "") or "").strip()
        if not nome_org:
            nome_org = "Organização Padrão"
        organizacao, _ = Organizacao.objects.get_or_create(
            nome=nome_org,
            defaults={"descricao": DESCRICAO_ORG_AUTOMATICA},
        )
        evento.organizacao_id = organizacao.id
        evento.organizador_fk_id = organizador_padrao.id
        evento.save(update_fields=["organizacao", "organizador_fk"])


def reverter_eventos(apps, schema_editor):
    """Restaura, de forma best-effort, o nome da organizacao no campo de texto."""
    Evento = apps.get_model("core", "Evento")
    for evento in list(Evento.objects.all()):
        nome = ""
        if getattr(evento, "organizacao_id", None):
            nome = evento.organizacao.nome
        evento.organizador = nome
        evento.save(update_fields=["organizador"])


class Migration(migrations.Migration):
    """Materializa o vinculo do evento com organizador (Usuario) e organizacao."""

    dependencies = [
        ("core", "0012_inscricao_avaliacao"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="evento",
            name="organizacao",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="eventos",
                to="core.organizacao",
                verbose_name="Organizacao",
            ),
        ),
        migrations.AddField(
            model_name="evento",
            name="organizador_fk",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="eventos_organizados",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Organizador",
            ),
        ),
        migrations.RunPython(converter_eventos, reverter_eventos),
        migrations.RemoveField(
            model_name="evento",
            name="organizador",
        ),
        migrations.RemoveField(
            model_name="evento",
            name="gestor",
        ),
        migrations.RenameField(
            model_name="evento",
            old_name="organizador_fk",
            new_name="organizador",
        ),
        migrations.AlterField(
            model_name="evento",
            name="organizacao",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="eventos",
                to="core.organizacao",
                verbose_name="Organizacao",
            ),
        ),
        migrations.AlterField(
            model_name="evento",
            name="organizador",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="eventos_organizados",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Organizador",
            ),
        ),
    ]
