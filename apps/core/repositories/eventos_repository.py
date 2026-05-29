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
- Alterado por `Welder60 <https://github.com/Welder60>`_ em 29 maio 2026
"""

from __future__ import annotations

from typing import List, Optional

try:
    from typing import Self
except ImportError:
    from typing import TypeVar
    Self = TypeVar("Self")  # type: ignore[assignment]

from apps.core.models.eventos_models import Evento

__version__ = "0.0.3"
__license__ = "AGPL V3"


class EventosRepository:
    """Repositorio para manipulacao de dados de Eventos."""

    @staticmethod
    def create(data: dict) -> Evento:
        """Cria um novo evento no banco de dados."""
        return Evento.objects.create(**data)

    @staticmethod
    def get_by_id(evento_id) -> Optional[Evento]:
        """Busca um evento pelo seu ID (UUID ou int)."""
        try:
            return Evento.objects.get(pk=evento_id)
        except Evento.DoesNotExist:
            return None

    @staticmethod
    def get_all() -> List[Evento]:
        """Retorna todos os eventos ordenados por data de realizacao."""
        return list(Evento.objects.select_related("organizador", "organizacao").all())

    @staticmethod
    def update(evento_id, data: dict) -> Optional[Evento]:
        """Atualiza um evento existente pelo ID."""
        try:
            evento = Evento.objects.get(pk=evento_id)
            for field, value in data.items():
                setattr(evento, field, value)
            evento.save()
            return evento
        except Evento.DoesNotExist:
            return None

    @staticmethod
    def delete(evento_id) -> bool:
        """Remove um evento pelo ID. Retorna True se deletado."""
        deleted, _ = Evento.objects.filter(pk=evento_id).delete()
        return deleted > 0
