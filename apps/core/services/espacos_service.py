"""
apps.core.services.espacos_service
====================================
Camada de serviço com as regras de negócio do domínio de Espaços Físicos.

Componentes Principais
----------------------
- :class:`EspacosService`: orquestra as operações de negócio delegando persistência
  ao :class:`~apps.core.repositories.espacos_repository.EspacosRepository`.

Notas
-----
- Requer Python >= 3.12
- Criado por `Welder60 <https://github.com/welder60>`_ em 01 junho 2026
"""

# compatibilidade
from __future__ import annotations

import uuid

from typing import List, Optional, Self

from apps.core.repositories.espacos_repository import EspacosRepository
from apps.core.models.espacos_models import EspacoFisico

__version__ = "0.0.1"
__license__ = "AGPL V3"


class EspacosService:
    """Serviço para regras de negócio de Espaços Físicos."""

    def __init__(self: Self, repository: EspacosRepository = None):
        """
        Inicializa o serviço com o repositório fornecido.

        :param repository: Instância do repositório de espaços. Se None,
                           usa EspacosRepository padrão.
        :type repository: EspacosRepository or None
        """
        self.repository = repository or EspacosRepository()

    def criar_espaco(self: Self, data: dict) -> EspacoFisico:
        """
        Cria um novo espaço físico após validação básica.

        :param data: Dicionário com os campos do espaço.
        :type data: dict
        :returns: Instância do espaço criado.
        :rtype: EspacoFisico
        :raises ValueError: Se o nome não for fornecido.
        """
        if not data.get("nome"):
            raise ValueError("O campo 'nome' é obrigatório.")
        return self.repository.create(data)

    def listar_espacos(self: Self) -> List[EspacoFisico]:
        """
        Retorna todos os espaços físicos cadastrados.

        :returns: Lista de instâncias de EspacoFisico.
        :rtype: list[EspacoFisico]
        """
        return self.repository.get_all()

    def obter_espaco(self: Self, espaco_id: uuid.UUID) -> Optional[EspacoFisico]:
        """
        Busca um espaço físico pelo UUID.

        :param espaco_id: Identificador UUID do espaço.
        :type espaco_id: uuid.UUID
        :returns: Instância do espaço ou None se não encontrado.
        :rtype: EspacoFisico or None
        """
        return self.repository.get_by_id(espaco_id)

    def atualizar_espaco(
        self: Self, espaco_id: uuid.UUID, data: dict
    ) -> Optional[EspacoFisico]:
        """
        Atualiza os dados de um espaço físico existente.

        :param espaco_id: Identificador UUID do espaço a atualizar.
        :type espaco_id: uuid.UUID
        :param data: Dicionário com os campos a atualizar.
        :type data: dict
        :returns: Instância atualizada ou None se não encontrado.
        :rtype: EspacoFisico or None
        """
        return self.repository.update(espaco_id, data)

    def remover_espaco(self: Self, espaco_id: uuid.UUID) -> bool:
        """
        Remove um espaço físico pelo UUID.

        :param espaco_id: Identificador UUID do espaço a remover.
        :type espaco_id: uuid.UUID
        :returns: True se removido, False se não encontrado.
        :rtype: bool
        """
        return self.repository.delete(espaco_id)
