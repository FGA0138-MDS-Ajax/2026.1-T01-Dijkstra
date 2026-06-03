"""
apps.core.services.organizacoes_service
=========================================
Camada de serviço com as regras de negócio do domínio de Organizações Esportivas.

Componentes Principais
----------------------
- :class:`OrganizacoesService`: orquestra as operações de negócio delegando
  persistência ao
  :class:`~apps.core.repositories.organizacoes_repository.OrganizacoesRepository`.

Notas
-----
- Requer Python >= 3.12
- Criado por `Welder60 <https://github.com/welder60>`_ em 02 junho 2026
"""

# compatibilidade
from __future__ import annotations

import uuid

from typing import List, Optional, Self

from apps.core.repositories.organizacoes_repository import OrganizacoesRepository
from apps.core.models.organizacoes_models import Organizacao

__version__ = "0.0.1"
__license__ = "AGPL V3"


class OrganizacoesService:
    """Serviço para regras de negócio de Organizações Esportivas."""

    def __init__(self: Self, repository: OrganizacoesRepository = None):
        """
        Inicializa o serviço com o repositório fornecido.

        :param repository: Instância do repositório de organizações. Se None,
                           usa OrganizacoesRepository padrão.
        :type repository: OrganizacoesRepository or None
        """
        self.repository = repository or OrganizacoesRepository()

    def criar_organizacao(self: Self, data: dict) -> Organizacao:
        """
        Cria uma nova organização após validação básica.

        :param data: Dicionário com os campos da organização.
        :type data: dict
        :returns: Instância da organização criada.
        :rtype: Organizacao
        :raises ValueError: Se o nome não for fornecido.
        """
        if not data.get("nome"):
            raise ValueError("O campo 'nome' é obrigatório.")
        return self.repository.create(data)

    def listar_organizacoes(self: Self) -> List[Organizacao]:
        """
        Retorna todas as organizações cadastradas.

        :returns: Lista de instâncias de Organizacao.
        :rtype: list[Organizacao]
        """
        return self.repository.get_all()

    def obter_organizacao(self: Self, organizacao_id: uuid.UUID) -> Optional[Organizacao]:
        """
        Busca uma organização pelo UUID.

        :param organizacao_id: Identificador UUID da organização.
        :type organizacao_id: uuid.UUID
        :returns: Instância da organização ou None se não encontrada.
        :rtype: Organizacao or None
        """
        return self.repository.get_by_id(organizacao_id)

    def atualizar_organizacao(
        self: Self, organizacao_id: uuid.UUID, data: dict
    ) -> Optional[Organizacao]:
        """
        Atualiza os dados de uma organização existente.

        :param organizacao_id: Identificador UUID da organização a atualizar.
        :type organizacao_id: uuid.UUID
        :param data: Dicionário com os campos a atualizar.
        :type data: dict
        :returns: Instância atualizada ou None se não encontrada.
        :rtype: Organizacao or None
        """
        return self.repository.update(organizacao_id, data)

    def remover_organizacao(self: Self, organizacao_id: uuid.UUID) -> bool:
        """
        Remove uma organização pelo UUID.

        :param organizacao_id: Identificador UUID da organização a remover.
        :type organizacao_id: uuid.UUID
        :returns: True se removida, False se não encontrada.
        :rtype: bool
        """
        return self.repository.delete(organizacao_id)
