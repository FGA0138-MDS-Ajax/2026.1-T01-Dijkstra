"""Repositorio de acesso a dados para o dominio de Eventos.

apps.core.repositories.eventos_repository
apps.core.repositories.eventos_repository
==========================================
Repositorio de acesso a dados para o dominio de Eventos.

Componentes Principais
----------------------
- :class:`EventosRepository`: encapsula as operacoes CRUD sobre
  :class:`~apps.core.models.eventos_models.Evento`.

Notas
-----
- Requer Python >= 3.12
- Criado por `MontMarcos <https://github.com/MontMarcos>`_ em 26 maio 2026
- Lint e testes por `Saresu <https://github.com/Saresu>`_ em 28 maio 2026
- Lint por Saresu 02 julho 2026
- Revisado por `Saresu <https://github.com/Saresu>`_ em 03 julho 2026
"""

from __future__ import annotations

import uuid
from typing import List, Optional, Self

from django.db.models import Q
from django.core.paginator import Paginator

from apps.core.models.eventos_models import Evento

__version__ = "0.0.5"
__license__ = "AGPL V3"


class EventosRepository:
    """Repositorio para manipulacao de dados de Eventos."""

    # definindo o usuario.
    def __init__(self: Self):
        self.usuario = None

    def create(self: Self, data: dict) -> Evento:
        """
        Cria um novo evento no banco de dados.

        :param data: Dicionario com os campos do evento.
        :type data: dict
        :returns: Instancia do evento criado.
        :rtype: Evento
        """
        return Evento.objects.create(**data)

    def get_by_id(self: Self, evento_id: uuid.UUID) -> Optional[Evento]:
        """
        Busca um evento pelo seu ID.

        :param evento_id: Identificador do evento.
        :type evento_id: uuid.UUID
        :returns: Instancia do evento ou None se nao encontrado.
        :rtype: Evento or None
        """
        try:
            return Evento.objects.get(id=evento_id)
        except Evento.DoesNotExist:
            return None

    def get_publicados(self) -> List[Evento]:
        """
        Retorna todos os eventos publicados.

        :returns: Lista de instancias de Evento.
        :rtype: list[Evento]
        """
        return list(Evento.objects.filter(status=Evento.Status.PUBLICADO))

    # def get_all(self) -> List[Evento]:
    #     """
    #     Retorna todos os eventos cadastrados.

    #     :returns: Lista de instancias de Evento.
    #     :rtype: list[Evento]
    #     """
    #     return list(Evento.objects.all())

    def get_all(self, page: Optional[int] = None, page_size: int = 20) -> List[Evento]:
        """
        Retorna todos os eventos cadastrados.

        Quando ``page`` nao e informado, mantem o comportamento historico
        de retornar a lista completa (uso interno/scripts). Quando ``page``
        e informado, retorna apenas a pagina solicitada, evitando carregar
        toda a tabela em memoria de uma vez.

        :param page: Numero da pagina (1-indexed). ``None`` retorna tudo.
        :type page: int or None
        :param page_size: Quantidade de itens por pagina.
        :type page_size: int
        :returns: Lista de instancias de Evento.
        :rtype: list[Evento]
        """
        queryset = Evento.objects.all().order_by("-criado_em")
        if page is None:
            return list(queryset)

        paginator = Paginator(queryset, page_size)
        return list(paginator.get_page(page).object_list)

    def update(self: Self, evento_id: uuid.UUID, data: dict) -> Optional[Evento]:
        """
        Atualiza os campos de um evento existente.

        :param evento_id: Identificador do evento a ser atualizado.
        :type evento_id: uuid.UUID
        :param data: Dicionario com os campos a atualizar.
        :type data: dict
        :returns: Instancia atualizada do evento ou None se nao encontrado.
        :rtype: Evento or None
        """
        evento = self.get_by_id(evento_id)
        if evento:
            for key, value in data.items():
                setattr(evento, key, value)
            evento.save()
            return evento
        return None

    def delete(self: Self, evento_id: uuid.UUID) -> bool:
        """
        Deleta um evento pelo seu ID.

        :param evento_id: Identificador do evento a ser deletado.
        :type evento_id: uuid.UUID
        :returns: True se deletado com sucesso, False se nao encontrado.
        :rtype: bool
        """
        evento = self.get_by_id(evento_id)
        if evento:
            evento.delete()
            return True
        return False

    def filter_events(
        self: Self,
        queryset,
        query: Optional[str] = None,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
    ):
        """
        Filtra um queryset de eventos por texto e intervalo de datas.

        :param queryset: Queryset original de eventos.
        :param query: Termo de busca para nome, descricao ou local.
        :param data_inicio: Data inicial do filtro.
        :param data_fim: Data final do filtro.
        :returns: Queryset filtrado.
        """
        if query:
            queryset = queryset.filter(
                Q(nome__icontains=query)
                | Q(descricao__icontains=query)
                | Q(local__icontains=query)
            )

        if data_inicio:
            queryset = queryset.filter(data__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(data__lte=data_fim)

        return queryset

    def filter_events_by_date(
        self: Self,
        queryset,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
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
