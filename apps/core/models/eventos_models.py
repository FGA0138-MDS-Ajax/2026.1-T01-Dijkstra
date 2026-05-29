"""
apps.core.models.eventos_models
================================
Model Django para o domínio de Eventos.

Componentes Principais
----------------------
- :class:`Evento`: representa um evento no sistema SIGEsporte.

Notas
-----
- Requer Python >= 3.12
- Criado por `MontMarcos <https://github.com/MontMarcos>`_ em 26 maio 2026
- Lint e testes por `Saresu <https://github.com/Saresu>`_ em 28 maio 2026
"""

# compatibilidade
from __future__ import annotations

from typing import Self

from django.db import models

__version__ = "0.0.2"
__license__ = "AGPL V3"


class Evento(models.Model):
    """
    Representa um evento no sistema SIGEsporte.

    :param nome: Nome do evento.
    :param data: Data de realização do evento.
    :param horario: Horário de realização do evento.
    :param local: Local de realização do evento.
    :param organizador: Nome do organizador responsável.
    :param gestor: Nome do gestor do evento.
    :param descricao: Descrição opcional do evento.
    :param capacidade: Número máximo de pessoas.
    :param imagem: Imagem ilustrativa do evento (opcional).
    :param criado_em: Data/hora de criação (preenchido automaticamente).
    :param atualizado_em: Data/hora da última atualização (preenchida automaticamente).
    """

    nome = models.CharField(max_length=100, verbose_name="Nome do Evento")
    data = models.DateField(verbose_name="Data do Evento")
    horario = models.TimeField(verbose_name="Horário do Evento")
    local = models.CharField(max_length=150, verbose_name="Local")
    organizador = models.CharField(max_length=100, verbose_name="Organizador")
    gestor = models.CharField(max_length=100, verbose_name="Gestor")
    descricao = models.TextField(verbose_name="Descrição", blank=True, null=True)
    capacidade = models.PositiveIntegerField(verbose_name="Capacidade de Pessoas")
    imagem = models.ImageField(
        upload_to="eventos/", verbose_name="Imagem do Evento", blank=True, null=True
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    # suprimindo too few por hora reanalisar depois
    class Meta:  # pylint: disable=too-few-public-methods
        """Metadados do model Evento."""

        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ["-data", "-horario"]

    # pylint: disable=invalid-str-returned
    def __str__(self: Self) -> str:
        return self.nome
