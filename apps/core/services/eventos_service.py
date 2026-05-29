"""
apps.core.services.eventos_service
====================================
Camada de servico com as regras de negocio do dominio de Eventos.
"""

from __future__ import annotations

from typing import List, Optional

try:
    from typing import Self
except ImportError:
    from typing import TypeVar
    Self = TypeVar("Self")  # type: ignore[assignment]

from apps.core.repositories.eventos_repository import EventosRepository
from apps.core.models.eventos_models import Evento

__version__ = "0.0.3"
__license__ = "AGPL V3"


class EventosService:
    """Servico para regras de negocio de Eventos."""

    def __init__(self, repository: EventosRepository = None):
        """Inicializa o servico com o repositorio fornecido."""
        self.repository = repository or EventosRepository()

    def criar_evento(self, data: dict) -> Evento:
        """Cria um novo evento."""
        return self.repository.create(data)

    def buscar_evento(self, evento_id) -> Optional[Evento]:
        """Busca um evento pelo ID."""
        return self.repository.get_by_id(evento_id)

    def listar_eventos(self) -> List[Evento]:
        """Lista todos os eventos."""
        return self.repository.get_all()

    def atualizar_evento(self, evento_id, data: dict) -> Optional[Evento]:
        """Atualiza um evento existente."""
        return self.repository.update(evento_id, data)

    def excluir_evento(self, evento_id) -> bool:
        """Remove um evento pelo ID."""
        return self.repository.delete(evento_id)
