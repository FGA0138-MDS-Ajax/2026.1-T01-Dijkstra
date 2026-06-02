"""
apps.core.repositories.organizacoes_repository
===============================================
Repositório de acesso a dados para o domínio de Organizações Esportivas.

Componentes Principais
----------------------
- :class:`OrganizacoesRepository`: encapsula as operações CRUD sobre
  :class:`~apps.core.models.organizacoes_models.Organizacao`.

Notas
-----
- Requer Python >= 3.12
- Criado por `Welder60 <https://github.com/welder60>`_ em 02 junho 2026
"""

# compatibilidade
from __future__ import annotations

import uuid

from typing import List, Optional

from apps.core.models.organizacoes_models import Organizacao

__version__ = "0.0.1"
__license__ = "AGPL V3"


class OrganizacoesRepository:
    """Repositório para manipulação de dados de Organizações Esportivas."""

    def create(self, data: dict) -> Organizacao:
        """
        Cria uma nova organização no banco de dados.

        :param data: Dicionário com os campos da organização.
        :type data: dict
        :returns: Instância da organização criada.
        :rtype: Organizacao
        """
        return Organizacao.objects.create(**data)

    def get_by_id(self, organizacao_id: uuid.UUID) -> Optional[Organizacao]:
        """
        Busca uma organização pelo seu UUID.

        :param organizacao_id: Identificador UUID da organização.
        :type organizacao_id: uuid.UUID
        :returns: Instância da organização ou None se não encontrada.
        :rtype: Organizacao or None
        """
        try:
            return Organizacao.objects.get(id=organizacao_id)
        except Organizacao.DoesNotExist:
            return None

    def get_all(self) -> List[Organizacao]:
        """
        Retorna todas as organizações cadastradas.

        :returns: Lista de instâncias de Organizacao.
        :rtype: list[Organizacao]
        """
        return list(Organizacao.objects.all())

    def update(self, organizacao_id: uuid.UUID, data: dict) -> Optional[Organizacao]:
        """
        Atualiza os campos de uma organização existente.

        :param organizacao_id: Identificador UUID da organização a atualizar.
        :type organizacao_id: uuid.UUID
        :param data: Dicionário com os campos a atualizar.
        :type data: dict
        :returns: Instância atualizada ou None se não encontrada.
        :rtype: Organizacao or None
        """
        organizacao = self.get_by_id(organizacao_id)
        if organizacao is None:
            return None
        for campo, valor in data.items():
            setattr(organizacao, campo, valor)
        organizacao.save()
        return organizacao

    def delete(self, organizacao_id: uuid.UUID) -> bool:
        """
        Remove uma organização do banco de dados.

        :param organizacao_id: Identificador UUID da organização a remover.
        :type organizacao_id: uuid.UUID
        :returns: True se removida com sucesso, False se não encontrada.
        :rtype: bool
        """
        organizacao = self.get_by_id(organizacao_id)
        if organizacao is None:
            return False
        organizacao.delete()
        return True
