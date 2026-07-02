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
- Revisado por `Saresu <https://github.com/Saresu>`_ em 02 julho 2026
"""

from __future__ import annotations

import uuid
from typing import List, Optional, Self, Any

from apps.core.repositories.organizacoes_repository import OrganizacoesRepository
from apps.core.models.organizacoes_models import Organizacao, UsuarioOrganizacao

__version__ = "0.0.4"
__license__ = "AGPL V3"


class OrganizacoesService:
    """Servico para regras de negocio de Organizacoes Esportivas."""

    repository: OrganizacoesRepository

    def __init__(
        self: Self, repository: Optional[OrganizacoesRepository] = None
    ) -> None:
        """Inicializa o servico injetando ou instanciando o repositorio."""
        self.repository = repository or OrganizacoesRepository()

    def criar_organizacao(self: Self, data: dict[str, Any]) -> Organizacao:
        """Valida as regras de negocio e encaminha a criacao da organizacao."""
        if not data.get("nome"):
            raise ValueError("O campo 'nome' e obrigatorio.")
        return self.repository.create(data)

    def listar_organizacoes(self: Self) -> List[Organizacao]:
        """Obtem a listagem completa de organizacoes cadastradas."""
        return self.repository.get_all()

    def obter_organizacao(
        self: Self, organizacao_id: uuid.UUID
    ) -> Optional[Organizacao]:
        """Recupera os detalhes de uma organizacao especifica por ID."""
        return self.repository.get_by_id(organizacao_id)

    def atualizar_organizacao(
        self: Self, organizacao_id: uuid.UUID, data: dict[str, Any]
    ) -> Optional[Organizacao]:
        """Atualiza os dados de uma organizacao existente no sistema."""
        return self.repository.update(organizacao_id, data)

    def remover_organizacao(self: Self, organizacao_id: uuid.UUID) -> bool:
        """Remove o registro de uma organizacao através do seu ID."""
        return self.repository.delete(organizacao_id)

    # ------------------------------------------------------------------
    # Membros
    # ------------------------------------------------------------------

    def listar_membros(
        self: Self, organizacao_id: uuid.UUID
    ) -> List[UsuarioOrganizacao]:
        """Retorna todos os membros vinculados a uma organizacao."""
        return self.repository.listar_membros(organizacao_id)

    def adicionar_membro(
        self: Self, organizacao_id: uuid.UUID, usuario_id: uuid.UUID
    ) -> UsuarioOrganizacao:
        """Vincula um novo usuario como membro de uma organizacao."""
        return self.repository.adicionar_membro(organizacao_id, usuario_id)

    def remover_membro(
        self: Self, organizacao_id: uuid.UUID, usuario_id: uuid.UUID
    ) -> bool:
        """Desvincula um membro de uma determinada organizacao."""
        return self.repository.remover_membro(organizacao_id, usuario_id)

    def listar_usuarios_sem_vinculo(self: Self, organizacao_id: uuid.UUID) -> List[Any]:
        """Retorna a lista de usuarios disponiveis para vinculo."""
        return self.repository.listar_usuarios_sem_vinculo(organizacao_id)

    def listar_organizacoes_do_usuario(
        self: Self, usuario_id: uuid.UUID
    ) -> List[Organizacao]:
        """Busca todas as organizacoes associadas a um perfil de usuario."""
        return self.repository.listar_organizacoes_do_usuario(usuario_id)
