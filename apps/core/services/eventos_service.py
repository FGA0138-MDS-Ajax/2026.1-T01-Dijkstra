from typing import List, Optional
from apps.core.repositories.eventos_repository import EventosRepository
from apps.core.models.eventos_models import Evento

class EventosService:
    """Serviço para regras de negócio de Eventos."""

    def __init__(self, repository: EventosRepository = None):
        self.repository = repository or EventosRepository()

    def criar_evento(self, data: dict) -> Evento:
        """Regra de negócio para criação de evento."""
        return self.repository.create(data)

    def buscar_evento(self, evento_id: int) -> Optional[Evento]:
        """Busca um evento específico."""
        return self.repository.get_by_id(evento_id)

    def listar_eventos(self) -> List[Evento]:
        """Lista todos os eventos cadastrados."""
        return self.repository.get_all()

    def atualizar_evento(self, evento_id: int, data: dict) -> Optional[Evento]:
        """Regra de negócio para atualização de evento."""
        return self.repository.update(evento_id, data)

    def excluir_evento(self, evento_id: int) -> bool:
        """Regra de negócio para exclusão de evento."""
        return self.repository.delete(evento_id)
