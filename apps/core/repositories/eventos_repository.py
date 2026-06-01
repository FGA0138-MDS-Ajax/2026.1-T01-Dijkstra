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
from django.db.models import Q
from apps.core.models.eventos_models import Evento

__version__ = "0.0.2"
__license__ = "AGPL V3"


class EventosRepository:
    """Repositório para manipulação de dados de Eventos."""

    def create(self, data: dict) -> Evento:
        """
        Cria um novo evento no banco de dados.

        :param data: Dicionário com os campos do evento.
        :type data: dict
        :returns: Instância do evento criado.
        :rtype: Evento
        """
        return Evento.objects.create(**data)  # expanxão implicita

    def get_by_id(self, evento_id: int) -> Optional[Evento]:
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

    def get_all(self) -> List[Evento]:
        """
        Retorna todos os eventos cadastrados.

        :returns: Lista de instâncias de Evento.
        :rtype: list[Evento]
        """
        return list(Evento.objects.all())

    def update(self, evento_id: int, data: dict) -> Optional[Evento]:
        """
        Atualiza os campos de um evento existente.

        :param evento_id: Identificador do evento a ser atualizado.
        :type evento_id: int
        :param data: Dicionário com os campos a atualizar.
        :type data: dict
        :returns: Instância atualizada do evento ou None se não encontrado.
        :rtype: Evento or None
        """

        evento = self.get_by_id(evento_id)
        if evento:
            for key, value in data.items():
                setattr(evento, key, value)
            evento.save()
            return evento
        return None

    def delete(self, evento_id: int) -> bool:
        """
        Deleta um evento pelo seu ID.

        :param evento_id: Identificador do evento a ser deletado.
        :type evento_id: int
        :returns: True se deletado com sucesso, False se não encontrado.
        :rtype: bool
        """
        evento = self.get_by_id(evento_id)
        if evento:
            evento.delete()
            return True
        return False

    def filter_events(
        self,
        queryset,
        query: Optional[str] = None,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None
    ):
        """
        Filtra um queryset de eventos por texto e intervalo de datas.

        :param queryset: Queryset original de eventos.
        :param query: Termo de busca para nome, descrição ou local.
        :param data_inicio: Data inicial do filtro.
        :param data_fim: Data final do filtro.
        :returns: Queryset filtrado.
        """

        if query:
            queryset = queryset.filter(
                Q(nome__icontains=query) |
                Q(descricao__icontains=query) |
                Q(local__icontains=query)
            )

        if data_inicio:
            queryset = queryset.filter(data__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(data__lte=data_fim)

        return queryset

    def filter_events_by_date(
        self, queryset, data_inicio: Optional[str] = None, data_fim: Optional[str] = None
    ) -> List[Evento]:
        """
        Filtra um queryset de eventos por um intervalo de datas.

        :param queryset: Queryset original de eventos.
        :param data_inicio: Data inicial do filtro.
        :param data_fim: Data final do filtro.
        :returns: Queryset filtrado.
        """
        if data_inicio:
            queryset = queryset.filter(data__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(data__lte=data_fim)
        return list(queryset)
