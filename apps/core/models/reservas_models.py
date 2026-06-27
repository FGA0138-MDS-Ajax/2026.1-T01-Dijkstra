"""Model Django para o dominio de Reservas de Espaço.

apps.core.models.reservas_models
=================================
Model Django para o dominio de Reservas de Espaço.

Componentes Principais
----------------------
- :class:`ReservaEspaco`: representa a solicitação de reserva de um espaço físico.

Notas
-----
- Requer Python >= 3.12
- Apenas gestores (tipo="GE") podem aprovar ou reprovar reservas.
- Apenas organizadores (tipo="OR") podem solicitar reservas.
- Reservas aprovadas impedem a criação e aprovação de reservas conflitantes
  (mesmo espaço com sobreposição de horário).
"""

from __future__ import annotations

import uuid
from typing import Self

from django.conf import settings
from django.db import models

from apps.core.models.espacos_models import EspacoFisico
from apps.core.models.eventos_models import Evento

__version__ = "0.0.1"
__license__ = "AGPL V3"


class ReservaEspaco(models.Model):
    """
    Representa a solicitação de reserva de um espaço físico para um evento.

    Um evento pode ter mais de uma reserva (em espaços ou horários diferentes).
    Reservas aprovadas bloqueiam a criação e a aprovação de novas reservas
    conflitantes (mesmo espaço, período sobreposto).

    :param id: Identificador único UUID gerado automaticamente.
    :param espaco: Espaço físico reservado.
    :param evento: Evento ao qual a reserva está vinculada.
    :param solicitante: Usuário organizador que solicitou a reserva.
    :param avaliador: Gestor que aprovou ou reprovou a reserva (nullable).
    :param status: Situação atual da reserva.
    :param data_inicio: Data/hora de início da reserva.
    :param data_fim: Data/hora de término da reserva.
    :param motivo_reprovacao: Justificativa do gestor em caso de reprovação (nullable).
    :param criado_em: Data/hora de criação (preenchida automaticamente).
    """

    class Status(models.TextChoices):
        """Situação da reserva de espaço."""

        PENDENTE = "pendente", "Pendente"
        APROVADA = "aprovada", "Aprovada"
        REPROVADA = "reprovada", "Reprovada"
        CANCELADA = "cancelada", "Cancelada"

    # pylint: disable=duplicate-code
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )
    espaco = models.ForeignKey(
        EspacoFisico,
        on_delete=models.CASCADE,
        related_name="reservas",
        verbose_name="Espaço Físico",
    )
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="reservas",
        verbose_name="Evento",
    )
    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservas_solicitadas",
        verbose_name="Solicitante",
    )
    avaliador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="reservas_avaliadas",
        verbose_name="Avaliador",
        blank=True,
        null=True,
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PENDENTE,
        verbose_name="Status",
    )
    data_inicio = models.DateTimeField(verbose_name="Data/Hora de Início")
    data_fim = models.DateTimeField(verbose_name="Data/Hora de Término")
    motivo_reprovacao = models.TextField(
        verbose_name="Motivo da Reprovação",
        blank=True,
        null=True,
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em",
    )

    class Meta:  # pylint: disable=too-few-public-methods
        """Metadados do model ReservaEspaco."""

        verbose_name = "Reserva de Espaço"
        verbose_name_plural = "Reservas de Espaço"
        ordering = ["-criado_em"]

    def __str__(self: Self) -> str:
        """Retorna a representação textual da reserva."""
        return (
            f"{self.espaco.nome} — {self.evento.nome} "
            f"({self.data_inicio:%d/%m/%Y %H:%M} → {self.data_fim:%H:%M})"
        )

    # ------------------------------------------------------------------
    # Detecção de conflito
    # ------------------------------------------------------------------

    @classmethod
    def tem_conflito(
        cls,
        espaco: EspacoFisico,
        data_inicio: object,
        data_fim: object,
        excluir_pk: uuid.UUID | None = None,
    ) -> bool:
        """
        Verifica se existe reserva APROVADA que conflita com o período informado.

        Dois períodos conflitam quando se sobrepõem: o início de um é anterior
        ao fim do outro e vice-versa.

        :param espaco: Espaço físico a verificar.
        :param data_inicio: Início do período candidato.
        :param data_fim: Fim do período candidato.
        :param excluir_pk: PK da reserva a ignorar na verificação (útil ao aprovar).
        :returns: True se houver conflito, False caso contrário.
        """
        qs = cls.objects.filter(
            espaco=espaco,
            status=cls.Status.APROVADA,
            data_inicio__lt=data_fim,
            data_fim__gt=data_inicio,
        )
        if excluir_pk is not None:
            qs = qs.exclude(pk=excluir_pk)
        return qs.exists()
