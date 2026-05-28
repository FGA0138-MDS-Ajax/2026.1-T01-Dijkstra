"""
apps.core.repositories.eventos_repository
==========================================
Repositório de acesso a dados para o domínio de Eventos.

Componentes Principais
----------------------
- :class:`EventosRepository`: encapsula as operações CRUD sobre 
  :class:`~apps.core.models.eventos_models.Evento`.

Notas
-----
- Requer Python >= 3.12
- Criado por `MontMarcos <https://github.com/MontMarcos>`_ em 26 maio 2026
- Lint e testes por `Saresu <https://github.com/Saresu>`_ em 28 maio 2026
"""

# compatibilidade
from __future__ import annotations


from typing import List, Optional
from apps.core.models.eventos_models import Evento

__version__ = "0.0.2"
__license__ = "AGPL V3"

class EventosRepository:
    """Repositório para manipulação de dados de Eventos."""

    @staticmethod
    def create(data: dict) -> Evento:
        """
        Cria um novo evento no banco de dados.

        :param data: Dicionário com os campos do evento.
        :type data: dict
        :returns: Instância do evento criado.
        :rtype: Evento
        """
        return Evento.objects.create(**data)  # expanção inplicita

    @staticmethod
    def get_by_id(evento_id: int) -> Optional[Evento]:
        """
        Busca um evento pelo seu ID.

        :param evento_id: Identificador do evento.
        :type evento_id: int
        :returns: Instância do evento ou None se não encontrado.
        :rtype: Evento or None
        """
        try:
            return Evento.objects.get(id=evento_id)
        except Evento.DoesNotExist:
            return None

    @staticmethod
    def get_all() -> List[Evento]:
        """
        Retorna todos os eventos cadastrados.

        :returns: Lista de instâncias de Evento.
        :rtype: list[Evento]
        """
        return list(Evento.objects.all())

    @staticmethod
    def update(evento_id: int, data: dict) -> Optional[Evento]:
        """
        Atualiza os campos de um evento existente.

        :param evento_id: Identificador do evento a ser atualizado.
        :type evento_id: int
        :param data: Dicionário com os campos a atualizar.
        :type data: dict
        :returns: Instância atualizada do evento ou None se não encontrado.
        :rtype: Evento or None
        """

        evento = EventosRepository.get_by_id(evento_id)
        if evento:
            for key, value in data.items():
                setattr(evento, key, value)
            evento.save()
            return evento
        return None

    @staticmethod
    def delete(evento_id: int) -> bool:
        """
        Deleta um evento pelo seu ID.

        :param evento_id: Identificador do evento a ser deletado.
        :type evento_id: int
        :returns: True se deletado com sucesso, False se não encontrado.
        :rtype: bool
        """
        evento = EventosRepository.get_by_id(evento_id)
        if evento:
            evento.delete()
            return True
        return False
