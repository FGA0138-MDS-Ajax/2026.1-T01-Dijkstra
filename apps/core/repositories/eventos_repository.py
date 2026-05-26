from typing import List, Optional
from apps.core.models.eventos_models import Evento

class EventosRepository:
    """Repositório para manipulação de dados de Eventos."""

    @staticmethod
    def create(data: dict) -> Evento:
        """Cria um novo evento."""
        return Evento.objects.create(**data)

    @staticmethod
    def get_by_id(evento_id: int) -> Optional[Evento]:
        """Busca um evento pelo ID."""
        try:
            return Evento.objects.get(id=evento_id)
        except Evento.DoesNotExist:
            return None

    @staticmethod
    def get_all() -> List[Evento]:
        """Retorna todos os eventos."""
        return list(Evento.objects.all())

    @staticmethod
    def update(evento_id: int, data: dict) -> Optional[Evento]:
        """Atualiza um evento existente."""
        evento = EventosRepository.get_by_id(evento_id)
        if evento:
            for key, value in data.items():
                setattr(evento, key, value)
            evento.save()
            return evento
        return None

    @staticmethod
    def delete(evento_id: int) -> bool:
        """Deleta um evento."""
        evento = EventosRepository.get_by_id(evento_id)
        if evento:
            evento.delete()
            return True
        return False
    