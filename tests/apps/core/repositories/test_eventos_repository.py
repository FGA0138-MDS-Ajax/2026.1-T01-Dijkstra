import uuid

from datetime import date, time
from unittest.mock import MagicMock

from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.core.models.eventos_models import Evento
from apps.core.models.organizacoes_models import Organizacao
from apps.core.repositories.eventos_repository import EventosRepository


class TestEventosRepositoryFiltros(TestCase):
    """Testes para o repositório de Eventos."""

    def setUp(self):
        Evento.objects.all().delete()
        self.repository = EventosRepository()
        self.organizador = get_user_model().objects.create_user(
            username="rep_org", password="senha123", tipo="OR",
        )
        self.organizacao = Organizacao.objects.create(
            nome="Organização Repo", descricao="Org de teste.",
        )
        self.evento_data = {
            "nome": "Evento Teste",
            "data": date(2023, 10, 27),
            "horario": time(14, 0),
            "local": "Local Teste",
            "organizador": self.organizador,
            "organizacao": self.organizacao,
            "descricao": "Descrição Teste",
            "capacidade": 100,
        }

    def test_create_evento(self):
        """Testa a criação de um evento."""
        evento = self.repository.create(self.evento_data)
        self.assertEqual(evento.nome, "Evento Teste")
        self.assertEqual(Evento.objects.count(), 1)

    def test_get_by_id(self):
        """Testa a busca de um evento pelo ID."""
        evento_criado = self.repository.create(self.evento_data)
        evento_buscado = self.repository.get_by_id(evento_criado.id)
        self.assertEqual(evento_buscado.id, evento_criado.id)

    def test_get_all(self):
        """Testa a listagem de todos os eventos."""
        self.repository.create(self.evento_data)
        self.repository.create({**self.evento_data, "nome": "Evento 2"})
        eventos = self.repository.get_all()
        self.assertEqual(len(eventos), 2)

    def test_update_evento(self):
        """Testa a atualização de um evento."""
        evento = self.repository.create(self.evento_data)
        updated_evento = self.repository.update(evento.id, {"nome": "Nome Atualizado"})
        self.assertEqual(updated_evento.nome, "Nome Atualizado")

    def test_delete_evento(self):
        """Testa a exclusão de um evento."""
        evento = self.repository.create(self.evento_data)
        success = self.repository.delete(evento.id)
        self.assertTrue(success)
        self.assertEqual(Evento.objects.count(), 0)

    def test_get_by_id_nao_encontrado(self):
        """get_by_id com id inexistente retorna None."""
        self.assertIsNone(self.repository.get_by_id(uuid.uuid4()))

    def test_update_nao_encontrado(self):
        """update com id inexistente retorna None."""
        self.assertIsNone(self.repository.update(uuid.uuid4(), {"nome": "X"}))

    def test_delete_nao_encontrado(self):
        """delete com id inexistente retorna False."""
        self.assertFalse(self.repository.delete(uuid.uuid4()))

    def test_filter_events_by_date(self):
        """Testa o filtro de eventos por data no repositório."""
        self.repository.create({**self.evento_data, "data": date(2023, 10, 1)})
        self.repository.create({**self.evento_data, "data": date(2023, 10, 15)})
        self.repository.create({**self.evento_data, "data": date(2023, 11, 1)})

        qs = Evento.objects.all()
        filtered = self.repository.filter_events_by_date(qs, "2023-10-01", "2023-10-31")
        self.assertEqual(len(filtered), 2)

    def test_filter_events_com_query(self):
        queryset = MagicMock()
        queryset.filter.return_value = queryset

        resultado = self.repository.filter_events(
            queryset,
            query="futebol",
        )

        self.assertEqual(resultado, queryset)
        self.assertTrue(queryset.filter.called)

    def test_filter_events_com_data_inicio(self):
        queryset = MagicMock()
        queryset.filter.return_value = queryset

        self.repository.filter_events(
            queryset,
            data_inicio="2026-01-01",
        )

        queryset.filter.assert_called_with(
            data__gte="2026-01-01",
        )

    def test_filter_events_com_data_fim(self):
        queryset = MagicMock()
        queryset.filter.return_value = queryset

        self.repository.filter_events(
            queryset,
            data_fim="2026-12-31",
        )

        queryset.filter.assert_called_with(
            data__lte="2026-12-31",
        )

    def test_filter_events_com_todos_os_filtros(self):
        queryset = MagicMock()
        queryset.filter.return_value = queryset

        resultado = self.repository.filter_events(
            queryset,
            query="futebol",
            data_inicio="2026-01-01",
            data_fim="2026-12-31",
        )

        self.assertEqual(resultado, queryset)

        self.assertGreaterEqual(
            queryset.filter.call_count,
            3,
        )
