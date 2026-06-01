from datetime import date, time

from django.test import TestCase

from apps.core.models.eventos_models import Evento
from apps.core.repositories.eventos_repository import EventosRepository


class EventosRepositoryTest(TestCase):
    """Testes para o repositório de Eventos."""

    def setUp(self):
        Evento.objects.all().delete()
        self.repository = EventosRepository()
        self.evento_data = {
            "nome": "Evento Teste",
            "data": date(2023, 10, 27),
            "horario": time(14, 0),
            "local": "Local Teste",
            "organizador": "Organizador Teste",
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
        updated_evento = self.repository.update(
            evento.id, {"nome": "Nome Atualizado"}
        )
        self.assertEqual(updated_evento.nome, "Nome Atualizado")

    def test_delete_evento(self):
        """Testa a exclusão de um evento."""
        evento = self.repository.create(self.evento_data)
        success = self.repository.delete(evento.id)
        self.assertTrue(success)
        self.assertEqual(Evento.objects.count(), 0)

    def test_get_by_id_nao_encontrado(self):
        """get_by_id com id inexistente retorna None."""
        self.assertIsNone(self.repository.get_by_id(99999))

    def test_update_nao_encontrado(self):
        """update com id inexistente retorna None."""
        self.assertIsNone(self.repository.update(99999, {"nome": "X"}))

    def test_delete_nao_encontrado(self):
        """delete com id inexistente retorna False."""
        self.assertFalse(self.repository.delete(99999))

    def test_str_evento(self):
        """__str__ retorna o nome do evento."""
        evento = self.repository.create(self.evento_data)
        self.assertEqual(str(evento), "Evento Teste")

    def test_filter_events_by_date(self):
        """Testa o filtro de eventos por data no repositório."""
        self.repository.create({**self.evento_data, "data": date(2023, 10, 1)})
        self.repository.create({**self.evento_data, "data": date(2023, 10, 15)})
        self.repository.create({**self.evento_data, "data": date(2023, 11, 1)})

        qs = Evento.objects.all()
        filtered = self.repository.filter_events_by_date(qs, "2023-10-01", "2023-10-31")
        self.assertEqual(len(filtered), 2)
