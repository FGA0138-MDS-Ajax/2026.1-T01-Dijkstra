"""Model Django para o dominio de Usuarios.

apps.security.models.usuario_models
apps.security.models.usuario_models
=====================================
Model Django para o dominio de Usuarios.

Componentes Principais
----------------------
- :class:`TipoPerfil`: enum com os perfis de acesso do sistema.
- :class:`Usuario`: model customizado que estende AbstractUser.

Notas
-----
- Requer Python >= 3.12
- Requer AUTH_USER_MODEL = 'security.Usuario' no settings.py
"""

from __future__ import annotations

import uuid
from typing import Self

from django.contrib.auth.models import AbstractUser
from django.db import models

__version__ = "0.0.1"
__license__ = "AGPL V3"


class TipoPerfil(models.TextChoices):
    """Perfis de acesso disponiveis no sistema."""

    ALUNO = "AL", "Aluno"
    ORGANIZADOR = "OR", "Organizador"
    GESTOR = "GE", "Gestor"
    ADMIN = "AD", "Administrador"


class Usuario(AbstractUser):
    """
    Representa um usuario do sistema SIGEsporte.

    Estende AbstractUser do Django, substituindo o modelo padrao.

    :param id: Identificador unico (UUID).
    :param nome_completo: Nome completo do usuario.
    :param matricula: Matricula institucional (opcional).
    :param tipo: Perfil de acesso (TipoPerfil).
    :param is_active: Indica se o usuario esta ativo.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )
    nome_completo = models.CharField(
        max_length=255,
        verbose_name="Nome Completo",
    )
    matricula = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Matricula",
    )
    tipo = models.CharField(
        max_length=2,
        choices=TipoPerfil,
        default=TipoPerfil.ALUNO,
        verbose_name="Tipo de Perfil",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo",
    )

    class Meta:  # pylint: disable=too-few-public-methods
        """Metadados do model Usuario."""

        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ["nome_completo"]

    def __str__(self: Self) -> str:
        """Retorna o nome completo como representacao textual."""
        return self.nome_completo

    @property
    def is_aluno(self: Self) -> bool:
        """Retorna True se o perfil do usuario for Aluno."""
        return self.tipo == TipoPerfil.ALUNO

    @property
    def is_organizador(self: Self) -> bool:
        """Retorna True se o perfil do usuario for Organizador."""
        return self.tipo == TipoPerfil.ORGANIZADOR

    @property
    def is_gestor(self: Self) -> bool:
        """Retorna True se o perfil do usuario for Gestor."""
        return self.tipo == TipoPerfil.GESTOR
