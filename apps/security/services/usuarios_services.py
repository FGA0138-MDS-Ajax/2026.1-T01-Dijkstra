"""
apps.security.services.usuarios_services
=========================================
Camada de servico com as regras de negocio do dominio de Usuarios.

Componentes Principais
----------------------
- UsuarioService: Orquestra operacoes do dominio de usuarios.

Notas
-----
- Requer Python >= 3.12
- Revisado por `Saresu <https://github.com/Saresu>`_ em 02 julho 2026
"""

# pylint: disable=too-few-public-methods

from __future__ import annotations

from typing import Self

from apps.security.repositories.usuarios_repositories import UsuarioRepository

__version__ = "0.0.2"
__license__ = "AGPL V3"


class UsuarioService:
    """Servico para regras de negocio de Usuários."""

    repository: UsuarioRepository

    def __init__(self: Self) -> None:
        """Inicializa o servico instanciando o repositorio padrao."""
        self.repository = UsuarioRepository()
