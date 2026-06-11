"""
apps.core.models.organizacoes_models
=====================================
Model Django para o dominio de Organizacoes Esportivas Universitarias.

Componentes Principais
----------------------
- Organizacao: representa uma organizacao esportiva universitaria no SIGEsporte.
- UsuarioOrganizacao: tabela associativa ManyToMany entre Usuario e Organizacao.

Notas
-----
- Requer Python >= 3.12
- Criado por Welder60 em 02 junho 2026
"""

# compatibilidade
from __future__ import annotations

import uuid

from typing import Self

from django.conf import settings
from django.db import models

__version__ = "0.0.2"
__license__ = "AGPL V3"


class Organizacao(models.Model):
    """Representa uma organizacao esportiva universitaria no sistema SIGEsporte."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )
    nome = models.CharField(max_length=150, verbose_name="Nome da Organizacao")
    descricao = models.TextField(verbose_name="Descricao")
    foto = models.ImageField(
        upload_to="organizacoes/",
        verbose_name="Foto da Organizacao",
        blank=True,
        null=True,
    )

    class Meta:  # pylint: disable=too-few-public-methods
        verbose_name = "Organizacao"
        verbose_name_plural = "Organizacoes"
        ordering = ["nome"]

    def __str__(self: Self) -> str:
        return self.nome


class UsuarioOrganizacao(models.Model):
    """Tabela associativa entre Usuario e Organizacao."""

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organizacoes_vinculadas",
        verbose_name="Usuario",
    )
    organizacao = models.ForeignKey(
        Organizacao,
        on_delete=models.CASCADE,
        related_name="membros",
        verbose_name="Organizacao",
    )

    class Meta:  # pylint: disable=too-few-public-methods
        verbose_name = "Membro de Organizacao"
        verbose_name_plural = "Membros de Organizacoes"
        unique_together = ("usuario", "organizacao")

    def __str__(self: Self) -> str:
        return f"{self.usuario} -> {self.organizacao}"
