"""
apps.core.models.organizacao_models
=====================================
Model Django para o domínio de Organizações.

Componentes Principais
----------------------
- :class:`Organizacao`: representa uma organização no sistema.
"""

from __future__ import annotations

import uuid
try:
    from typing import Self
except ImportError:  # Python < 3.11
    from typing import TypeVar
    Self = TypeVar("Self")  # type: ignore[assignment]

from django.conf import settings
from django.db import models

__version__ = "0.1.0"
__license__ = "AGPL V3"


class Organizacao(models.Model):
    """
    Representa uma organização que pode criar e gerir eventos.

    :param id: Identificador único (UUID).
    :param nome: Nome da organização.
    :param descricao: Descrição detalhada.
    :param foto: Logotipo ou imagem da organização (opcional).
    :param membros: Usuários membros da organização (M2M).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=255, verbose_name="Nome")
    descricao = models.TextField(verbose_name="Descrição")
    foto = models.ImageField(
        upload_to="organizacoes/fotos/",
        blank=True,
        null=True,
        verbose_name="Foto",
    )
    membros = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="organizacoes",
        blank=True,
        verbose_name="Membros",
    )

    class Meta:  # pylint: disable=too-few-public-methods
        """Metadados do model Organizacao."""

        verbose_name = "Organização"
        verbose_name_plural = "Organizações"
        ordering = ["nome"]

    def __str__(self: Self) -> str:
        return self.nome
