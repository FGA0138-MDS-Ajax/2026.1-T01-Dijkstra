"""Camada de servico com as regras de negocio do dominio de Eventos.

apps.core.services.eventos_service
apps.core.services.eventos_service
====================================
Camada de servico com as regras de negocio do dominio de Eventos.

Componentes Principais
----------------------
- :class:`EventosService`: orquestra as operacoes de negocio delegando
  persistencia ao
  :class:`~apps.core.repositories.eventos_repository.EventosRepository`.

Notas
-----
- Requer Python >= 3.12
- Criado por `MontMarcos <https://github.com/MontMarcos>`_ em 26 maio 2026
- Lint e testes por `Saresu <https://github.com/Saresu>`_ em 28 maio 2026
- Revisado por `Gui-fga <https://github.com/Gui-fga>`_ em 30 maio 2026
- Revisado por `Saresu <https://github.com/Saresu>`_ em 30 maio 2026
"""

from __future__ import annotations

import uuid
from typing import List, Optional, Self

from apps.core.models.eventos_models import Evento
from apps.core.repositories.eventos_repository import EventosRepository

__version__ = "0.0.3"
__license__ = "AGPL V3"


class EventosService:
    """Servico para regras de negocio de Eventos."""

    def __init__(self: Self, repository: EventosRepository = None):
        """
        Inicializa o servico com o repositorio fornecido.

        :param repository:
            Instancia do repositorio de eventos.
            Se None, usa EventosRepository padrao.
        :type repository: EventosRepository or None
        """
        self.repository = repository or EventosRepository()

    def criar_evento(self: Self, data: dict) -> Evento:
        """
        Cria um novo evento.

        :param data: Dicionario com os campos do evento.
        :type data: dict
        :returns: Instancia do evento criado.
        :rtype: Evento
        """
        return self.repository.create(data)

    def buscar_evento(self: Self, evento_id: uuid.UUID) -> Optional[Evento]:
        """
        Busca um evento pelo seu ID.

        :param evento_id: Identificador do evento.
        :type evento_id: uuid.UUID
        :returns: Instancia do evento ou None se nao encontrado.
        :rtype: Evento or None
        """
        return self.repository.get_by_id(evento_id)

    def listar_eventos(self: Self) -> List[Evento]:
        """
        Retorna todos os eventos cadastrados.

        :returns: Lista de instancias de Evento.
        :rtype: list[Evento]
        """
        return self.repository.get_all()

    def atualizar_evento(
        self: Self, evento_id: uuid.UUID, data: dict
    ) -> Optional[Evento]:
        """
        Atualiza os campos de um evento existente.

        :param evento_id: Identificador do evento a ser atualizado.
        :type evento_id: uuid.UUID
        :param data: Dicionario com os campos a atualizar.
        :type data: dict
        :returns: Instancia atualizada ou None se nao encontrado.
        :rtype: Evento or None
        """
        return self.repository.update(evento_id, data)

    def excluir_evento(self: Self, evento_id: uuid.UUID) -> bool:
        """
        Exclui um evento pelo seu ID.

        :param evento_id: Identificador do evento a ser excluido.
        :type evento_id: uuid.UUID
        :returns: True se excluido com sucesso, False se nao encontrado.
        :rtype: bool
        """
        return self.repository.delete(evento_id)

    def get_filtered_events(
        self: Self,
        query=None,
        data_inicio=None,
        data_fim=None,
    ):
        """
        Retorna eventos filtrados por texto e intervalo de datas.

        :param query: Termo de busca (opcional).
        :param data_inicio: Data inicial do intervalo (opcional).
        :param data_fim: Data final do intervalo (opcional).
        :returns: QuerySet de eventos filtrados.
        """
        eventos = Evento.objects.all()
        return self.repository.filter_events(
            eventos, query, data_inicio, data_fim
        )
