"""
apps.core.services.organizacoes_service
=========================================
Camada de servico com as regras de negocio do dominio de Organizacoes Esportivas.

Componentes Principais
----------------------
- OrganizacoesService: orquestra operacoes delegando persistencia ao
  OrganizacoesRepository, incluindo gestao de membros via UsuarioOrganizacao.

Notas
-----
- Requer Python >= 3.12
- Criado por Welder60 em 02 junho 2026
"""

from __future__ import annotations

import uuid
from typing import List, Optional, Self

from apps.core.repositories.organizacoes_repository import OrganizacoesRepository
from apps.core.models.organizacoes_models import Organizacao, UsuarioOrganizacao

__version__ = "0.0.2"
__license__ = "AGPL V3"


class OrganizacoesService:
    """Servico para regras de negocio de Organizacoes Esportivas."""

    def __init__(self: Self, repository: OrganizacoesRepository = None):
        self.repository = repository or OrganizacoesRepository()

    def criar_organizacao(self: Self, data: dict) -> Organizacao:
        if not data.get("nome"):
            raise ValueError("O campo 'nome' e obrigatorio.")
        return self.repository.create(data)

    def listar_organizacoes(self: Self) -> List[Organizacao]:
        return self.repository.get_all()

    def obter_organizacao(self: Self, organizacao_id: uuid.UUID) -> Optional[Organizacao]:
        return self.repository.get_by_id(organizacao_id)

    def atualizar_organizacao(
        self: Self, organizacao_id: uuid.UUID, data: dict
    ) -> Optional[Organizacao]:
        return self.repository.update(organizacao_id, data)

    def remover_organizacao(self: Self, organizacao_id: uuid.UUID) -> bool:
        return self.repository.delete(organizacao_id)

    # ------------------------------------------------------------------
    # Membros
    # ------------------------------------------------------------------

    def listar_membros(self: Self, organizacao_id: uuid.UUID) -> List:
        return self.repository.listar_membros(organizacao_id)

    def adicionar_membro(
        self: Self, organizacao_id: uuid.UUID, usuario_id: uuid.UUID
    ) -> UsuarioOrganizacao:
        return self.repository.adicionar_membro(organizacao_id, usuario_id)

    def remover_membro(
        self: Self, organizacao_id: uuid.UUID, usuario_id: uuid.UUID
    ) -> bool:
        return self.repository.remover_membro(organizacao_id, usuario_id)

    def listar_usuarios_sem_vinculo(self: Self, organizacao_id: uuid.UUID) -> List:
        return self.repository.listar_usuarios_sem_vinculo(organizacao_id)

    def listar_organizacoes_do_usuario(
        self: Self, usuario_id: uuid.UUID
    ) -> List[Organizacao]:
        return self.repository.listar_organizacoes_do_usuario(usuario_id)
