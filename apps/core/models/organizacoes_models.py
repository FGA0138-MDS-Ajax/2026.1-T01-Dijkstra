"""
apps.core.models.organizacoes_models
=====================================
Model Django para o domínio de Organizações Esportivas Universitárias.

Componentes Principais
----------------------
- :class:`Organizacao`: representa uma organização esportiva universitária
  no sistema SIGEsporte.

Notas
-----
- Requer Python >= 3.12
- Criado por `Welder60 <https://github.com/welder60>`_ em 02 junho 2026
"""

# compatibilidade
from __future__ import annotations

import uuid

from typing import Self

from django.db import models

__version__ = "0.0.1"
__license__ = "AGPL V3"


class Organizacao(models.Model):
    """
    Representa uma organização esportiva universitária no sistema SIGEsporte.

    :param id: Identificador único UUID gerado automaticamente.
    :param nome: Nome da organização.
    :param descricao: Descrição detalhada da organização.
    :param foto: Imagem ilustrativa da organização (opcional).
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )
    nome = models.CharField(max_length=150, verbose_name="Nome da Organização")
    descricao = models.TextField(verbose_name="Descrição")
    foto = models.ImageField(
        upload_to="organizacoes/",
        verbose_name="Foto da Organização",
        blank=True,
        null=True,
    )

    class Meta:  # pylint: disable=too-few-public-methods
        """Metadados do model Organizacao."""

        verbose_name = "Organização"
        verbose_name_plural = "Organizações"
        ordering = ["nome"]

    def __str__(self: Self) -> str:
        """Retorna o nome da organização como representação textual."""
        return self.nome
