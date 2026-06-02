"""
apps.core.models.espacos_models
================================
Model Django para o domínio de Espaços Físicos.

Componentes Principais
----------------------
- :class:`EspacoFisico`: representa um espaço físico/esportivo no sistema SIGEsporte.

Notas
-----
- Requer Python >= 3.12
- Criado por `Welder60 <https://github.com/welder60>`_ em 01 abril 2026
"""

# compatibilidade
from __future__ import annotations

import uuid

from typing import Self

from django.db import models

__version__ = "0.0.1"
__license__ = "AGPL V3"


class EspacoFisico(models.Model):
    """
    Representa um espaço físico/esportivo no sistema SIGEsporte.

    :param id: Identificador único UUID gerado automaticamente.
    :param nome: Nome do espaço físico.
    :param foto: Imagem ilustrativa do espaço (opcional).
    :param localizacao: Localização/endereço do espaço físico.
    :param descricao: Descrição detalhada do espaço físico.
    :param status: Situação atual do espaço (Disponível, Em Manutenção ou Desativado).
    :param criado_em: Data/hora de criação (preenchido automaticamente).
    :param atualizado_em: Data/hora da última atualização (preenchida automaticamente).
    """

    class Status(models.TextChoices):
        """Opções de status do espaço físico."""

        DISPONIVEL = "disponivel", "Disponível"
        EM_MANUTENCAO = "em_manutencao", "Em Manutenção"
        DESATIVADO = "desativado", "Desativado"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )
    nome = models.CharField(max_length=150, verbose_name="Nome do Espaço")
    foto = models.ImageField(
        upload_to="espacos/",
        verbose_name="Foto do Espaço",
        blank=True,
        null=True,
    )
    localizacao = models.TextField(verbose_name="Localização")
    descricao = models.TextField(verbose_name="Descrição")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DISPONIVEL,
        verbose_name="Status",
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:  # pylint: disable=too-few-public-methods
        """Metadados do model EspacoFisico."""

        verbose_name = "Espaço Físico"
        verbose_name_plural = "Espaços Físicos"
        ordering = ["nome"]

    def __str__(self: Self) -> str:
        """Retorna o nome do espaço físico como representação textual."""
        return self.nome

    @property
    def status_display(self: Self) -> str:
        """Retorna o rótulo legível do status atual."""
        return self.get_status_display()

    @property
    def status_css_class(self: Self) -> str:
        """Retorna a classe CSS correspondente ao status para exibição visual."""
        mapa = {
            self.Status.DISPONIVEL: "status-disponivel",
            self.Status.EM_MANUTENCAO: "status-manutencao",
            self.Status.DESATIVADO: "status-desativado",
        }
        return mapa.get(self.status, "")
