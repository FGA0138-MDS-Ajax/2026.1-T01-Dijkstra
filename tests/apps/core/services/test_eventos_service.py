from django.test import TestCase

from unittest.mock import MagicMock

from apps.core.services.eventos_service import EventosService
from apps.core.repositories.eventos_repository import EventosRepository
# from apps.core.models.eventos_models import Evento


class EventosServiceTest(TestCase):
    """Testes para o serviço de Eventos."""

    def setUp(self):
        self.repository_mock = MagicMock(spec=EventosRepository)
        self.service = EventosService(repository=self.repository_mock)

    def test_criar_evento(self):
        data = {"nome": "Teste"}
        self.service.criar_evento(data)
        self.repository_mock.create.assert_called_once_with(data)

    def test_buscar_evento(self):
        self.service.buscar_evento(1)
        self.repository_mock.get_by_id.assert_called_once_with(1)

    def test_listar_eventos(self):
        self.service.listar_eventos()
        self.repository_mock.get_all.assert_called_once()

    def test_atualizar_evento(self):
        data = {"nome": "Novo"}
        self.service.atualizar_evento(1, data)
        self.repository_mock.update.assert_called_once_with(1, data)

    def test_excluir_evento(self):
        self.service.excluir_evento(1)
        self.repository_mock.delete.assert_called_once_with(1)

    def test_get_filtered_events(self):
        """Verifica se o serviço chama o repositório para filtrar eventos."""
        self.service.get_filtered_events(
            data_inicio="2023-10-01", data_fim="2023-10-31"
        )
        # Nota: O service chama Evento.objects.all() internamente antes do repo.
        # Mas o mock deve ser chamado.
        self.repository_mock.filter_events.assert_called_once()
