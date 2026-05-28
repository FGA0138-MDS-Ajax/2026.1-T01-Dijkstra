"""
apps.core.services.eventos_service
====================================
Camada de serviço com as regras de negócio do domínio de Eventos.

Componentes Principais
----------------------
- :class:`EventosService`: orquestra as operações de negócio delegando persistência
ao :class:`~apps.core.repositories.eventos_repository.EventosRepository`.

Notas
-----
- Requer Python >= 3.12
- Criado por `MontMarcos <https://github.com/MontMarcos>`_ em 26 maio 2026
- Lint e testes por `Saresu <https://github.com/Saresu>`_ em 28 maio 2026
"""

# compatibilidade
from __future__ import annotations

from typing import List, Optional, Self
from apps.core.repositories.eventos_repository import EventosRepository
from apps.core.models.eventos_models import Evento

__version__ = "0.0.2"
__license__ = "AGPL V3"


class EventosService:
    """Serviço para regras de negócio de Eventos."""

    def __init__(self: Self, repository: EventosRepository = None):
        """
        Inicializa o serviço com o repositório fornecido.

        :param repository: Instância do repositório de eventos. Se None,
                            usa EventosRepository padrão.
        :type repository: EventosRepository or None
        """
        self.repository = repository or EventosRepository()

    def criar_evento(self: Self, data: dict) -> Evento:
        """
        Cria um novo evento.

        :param data: Dicionário com os dados do evento.
        :type data: dict
        :returns: Instância do evento criado.
        :rtype: Evento
        """
        return self.repository.create(data)

    def buscar_evento(self: Self, evento_id: int) -> Optional[Evento]:
        """
        Busca um evento pelo ID.

        :param evento_id: Identificador do evento.
        :type evento_id: int
        :returns: Instância do evento ou None se não encontrado.
        :rtype: Evento or None
        """
        return self.repository.get_by_id(evento_id)

    def listar_eventos(self: Self) -> List[Evento]:
        """
        Lista todos os eventos cadastrados.

        :returns: Lista de instâncias de Evento.
        :rtype: list[Evento]
        """

        return self.repository.get_all()

    def atualizar_evento(self: Self, evento_id: int, data: dict) -> Optional[Evento]:
        """
        Atualiza um evento existente.

        :param evento_id: Identificador do evento a ser atualizado.
        :type evento_id: int
        :param data: Dicionário com os campos a atualizar.
        :type data: dict
        :returns: Instância atualizada do evento ou None se não encontrado.
        :rtype: Evento or None
        """

        return self.repository.update(evento_id, data)

    def excluir_evento(self: Self, evento_id: int) -> bool:
        """
        Exclui um evento pelo ID.

        :param evento_id: Identificador do evento a ser excluído.
        :type evento_id: int
        :returns: True se excluído com sucesso, False se não encontrado.
        :rtype: bool
        """

        return self.repository.delete(evento_id)
