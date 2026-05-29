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
- Alterado por `Welder60 <https://github.com/Welder60>`_ em 29 maio 2026
"""

from __future__ import annotations

import uuid

try:
    from typing import Self
except ImportError:
    from typing import TypeVar
    Self = TypeVar("Self")  # type: ignore[assignment]

from django.conf import settings
from django.db import models

__version__ = "0.1.0"
__license__ = "AGPL V3"


class Evento(models.Model):
    """Representa um evento no sistema."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    titulo = models.CharField(max_length=255, verbose_name="Titulo")
    descricao = models.TextField(verbose_name="Descricao")
    foto = models.ImageField(
        upload_to="eventos/fotos/",
        blank=True,
        null=True,
        verbose_name="Foto",
    )
    data_realizacao = models.DateTimeField(verbose_name="Data de Realizacao")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    organizador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="eventos_criados",
        verbose_name="Organizador",
    )
    organizacao = models.ForeignKey(
        "core.Organizacao",
        on_delete=models.CASCADE,
        related_name="eventos",
        verbose_name="Organizacao",
    )

    class Meta:  # pylint: disable=too-few-public-methods
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ["-data_realizacao"]

    def __str__(self):
        return self.titulo
