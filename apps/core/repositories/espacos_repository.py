"""
apps.core.repositories.espacos_repository
==========================================
Repositório de acesso a dados para o domínio de Espaços Físicos.

Componentes Principais
----------------------
- :class:`EspacosRepository`: encapsula as operações CRUD sobre
  :class:`~apps.core.models.espacos_models.EspacoFisico`.

Notas
-----
- Requer Python >= 3.12
- Criado por `Welder60 <https://github.com/welder60>`_ em 01 abril 2026
"""

# compatibilidade
from __future__ import annotations

import uuid

from typing import List, Optional

from apps.core.models.espacos_models import EspacoFisico

__version__ = "0.0.1"
__license__ = "AGPL V3"


class EspacosRepository:
    """Repositório para manipulação de dados de Espaços Físicos."""

    def create(self, data: dict) -> EspacoFisico:
        """
        Cria um novo espaço físico no banco de dados.

        :param data: Dicionário com os campos do espaço.
        :type data: dict
        :returns: Instância do espaço criado.
        :rtype: EspacoFisico
        """
        return EspacoFisico.objects.create(**data)

    def get_by_id(self, espaco_id: uuid.UUID) -> Optional[EspacoFisico]:
        """
        Busca um espaço físico pelo seu UUID.

        :param espaco_id: Identificador UUID do espaço.
        :type espaco_id: uuid.UUID
        :returns: Instância do espaço ou None se não encontrado.
        :rtype: EspacoFisico or None
        """
        try:
            return EspacoFisico.objects.get(id=espaco_id)
        except EspacoFisico.DoesNotExist:
            return None

    def get_all(self) -> List[EspacoFisico]:
        """
        Retorna todos os espaços físicos cadastrados.

        :returns: Lista de instâncias de EspacoFisico.
        :rtype: list[EspacoFisico]
        """
        return list(EspacoFisico.objects.all())

    def update(self, espaco_id: uuid.UUID, data: dict) -> Optional[EspacoFisico]:
        """
        Atualiza os campos de um espaço físico existente.

        :param espaco_id: Identificador UUID do espaço a atualizar.
        :type espaco_id: uuid.UUID
        :param data: Dicionário com os campos a atualizar.
        :type data: dict
        :returns: Instância atualizada ou None se não encontrado.
        :rtype: EspacoFisico or None
        """
        espaco = self.get_by_id(espaco_id)
        if espaco is None:
            return None
        for campo, valor in data.items():
            setattr(espaco, campo, valor)
        espaco.save()
        return espaco

    def delete(self, espaco_id: uuid.UUID) -> bool:
        """
        Remove um espaço físico do banco de dados.

        :param espaco_id: Identificador UUID do espaço a remover.
        :type espaco_id: uuid.UUID
        :returns: True se removido com sucesso, False se não encontrado.
        :rtype: bool
        """
        espaco = self.get_by_id(espaco_id)
        if espaco is None:
            return False
        espaco.delete()
        return True
