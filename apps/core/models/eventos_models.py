"""Model Django para o dominio de Eventos.

apps.core.models.eventos_models
apps.core.models.eventos_models
================================
Model Django para o dominio de Eventos.

Componentes Principais
----------------------
- :class:`Evento`: representa um evento no sistema SIGEsporte.

Notas
-----
- Requer Python >= 3.12
- Criado por `MontMarcos <https://github.com/MontMarcos>`_ em 26 maio 2026
- Lint e testes por `Saresu <https://github.com/Saresu>`_ em 28 maio 2026
- Alerado por `Welder60 <https://github.com/welder60>`_ em 02 junho 2026
- Lint por `Saresu <https://github.com/Saresu>`_ em 05 junho 2026
- Vinculo a organizador (Usuario) e organizacao por
  `Welder60 <https://github.com/welder60>`_ em 23 junho 2026
"""

from __future__ import annotations

import uuid
from typing import Self

from django.conf import settings
from django.db import models

__version__ = "0.0.5"
__license__ = "AGPL V3"


class Evento(models.Model):
    """
    Representa um evento no sistema SIGEsporte.

    :param nome: Nome do evento.
    :param data: Data de realizacao do evento.
    :param horario: Horario de realizacao do evento.
    :param local: Local de realizacao do evento.
    :param organizador: Usuario que cria/organiza o evento.
    :param organizacao: Organizacao a qual o evento esta vinculado.
    :param descricao: Descricao opcional do evento.
    :param capacidade: Numero maximo de pessoas.
    :param imagem: Imagem ilustrativa do evento (opcional).
    :param status: Situacao de publicacao do evento (Rascunho ou Publicado).
    :param criado_em: Data/hora de criacao (preenchido automaticamente).
    :param atualizado_em:
        Data/hora da ultima atualizacao (preenchida automaticamente).
    """

    class Status(models.TextChoices):
        """Situacao de publicacao do evento."""

        RASCUNHO = "rascunho", "Rascunho"
        PUBLICADO = "publicado", "Publicado"

    # pylint: disable=duplicate-code
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )
    nome = models.CharField(max_length=100, verbose_name="Nome do Evento")
    data = models.DateField(verbose_name="Data do Evento")
    horario = models.TimeField(verbose_name="Horario do Evento")
    local = models.CharField(max_length=150, verbose_name="Local")
    organizador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="eventos_organizados",
        verbose_name="Organizador",
    )
    organizacao = models.ForeignKey(
        "core.Organizacao",
        on_delete=models.PROTECT,
        related_name="eventos",
        verbose_name="Organizacao",
    )
    descricao = models.TextField(verbose_name="Descricao", blank=True, null=True)
    capacidade = models.PositiveIntegerField(verbose_name="Capacidade de Pessoas")
    vagas_ocupadas = models.PositiveIntegerField(default=0, verbose_name="Vagas Ocupadas")
    imagem = models.ImageField(
        upload_to="eventos/",
        verbose_name="Imagem do Evento",
        blank=True,
        null=True,
    )
    status = models.CharField(
        max_length=10,
        choices=Status,
        default=Status.RASCUNHO,
        verbose_name="Status",
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:  # pylint: disable=too-few-public-methods
        """Metadados do model Evento."""

        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ["-data", "-horario"]

    def __str__(self: Self) -> str:  # pylint: disable=invalid-str-returned
        """Retorna o nome do evento como representacao textual."""
        return self.nome
