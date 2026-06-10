"""Model Django para o dominio de Inscrições.

apps.core.models.inscricao_models
apps.core.models.inscricao_models
==================================
Model Django para o dominio de Inscrições.

Componentes Principais
----------------------
- :class:`Inscricao`: representa a inscrição de um usuário em um evento.

Notas
-----
- Requer Python >= 3.12
- Criado por `DaviiGualbertoo <https://github.com/DaviiGualbertoo>`_ em 08 junho 2026
"""

from __future__ import annotations

import uuid
from typing import Self

from django.conf import settings
from django.db import models

from apps.core.models.eventos_models import Evento

__version__ = "0.0.1"
__license__ = "AGPL V3"


class Inscricao(models.Model):
    """
    Representa a inscrição de um aluno em um evento no sistema SIGEsporte.

    :param id: Identificador único da inscrição.
    :param aluno: Usuário (aluno) associado à inscrição.
    :param evento: Evento ao qual o aluno está inscrito.
    :param status: Situação atual da inscrição (Pendente, Aprovada, etc.).
    :param data_solicitacao: Data/hora em que a inscrição foi solicitada.
    """

    class Status(models.TextChoices):
        """Situação da aprovação da inscrição."""

        PENDENTE = "pendente", "Pendente"
        APROVADA = "aprovada", "Aprovada"
        REJEITADA = "rejeitada", "Rejeitada"
        CANCELADA = "cancelada", "Cancelada"

    # pylint: disable=duplicate-code
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )
    aluno = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="inscricoes",
        verbose_name="Aluno",
    )
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="inscricoes",
        verbose_name="Evento",
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PENDENTE,
        verbose_name="Status",
    )
    data_solicitacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data da Solicitação",
    )

    class Meta:  # pylint: disable=too-few-public-methods
        """Metadados do model Inscricao."""

        verbose_name = "Inscrição"
        verbose_name_plural = "Inscrições"
        unique_together = ("aluno", "evento")

    def __str__(self: Self) -> str:  # pylint: disable=invalid-str-returned
        """Retorna a representacao textual da inscricao."""
        return f"{self.aluno} -> {self.evento.nome} ({self.get_status_display()})"
    
   