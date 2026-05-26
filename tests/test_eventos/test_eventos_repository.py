from django.test import TestCase
from apps.core.models.eventos_models import Evento
from apps.core.repositories.eventos_repository import EventosRepository
from datetime import date, time

class EventosRepositoryTest(TestCase):
    """Testes para o repositório de Eventos."""

    def setUp(self):
        self.evento_data = {
            'nome': 'Evento Teste',
            'data': date(2023, 10, 27),
            'horario': time(14, 0),
            'local': 'Local Teste',
            'organizador': 'Organizador Teste',
            'descricao': 'Descrição Teste',
            'capacidade': 100
        }

    def test_create_evento(self):
        """Testa a criação de um evento."""
        evento = EventosRepository.create(self.evento_data)
        self.assertEqual(evento.nome, 'Evento Teste')
        self.assertEqual(Evento.objects.count(), 1)

    def test_get_by_id(self):
        """Testa a busca de um evento pelo ID."""
        evento_criado = EventosRepository.create(self.evento_data)
        evento_buscado = EventosRepository.get_by_id(evento_criado.id)
        self.assertEqual(evento_buscado.id, evento_criado.id)

    def test_get_all(self):
        """Testa a listagem de todos os eventos."""
        EventosRepository.create(self.evento_data)
        EventosRepository.create({**self.evento_data, 'nome': 'Evento 2'})
        eventos = EventosRepository.get_all()
        self.assertEqual(len(eventos), 2)

    def test_update_evento(self):
        """Testa a atualização de um evento."""
        evento = EventosRepository.create(self.evento_data)
        updated_evento = EventosRepository.update(evento.id, {'nome': 'Nome Atualizado'})
        self.assertEqual(updated_evento.nome, 'Nome Atualizado')

    def test_delete_evento(self):
        """Testa a exclusão de um evento."""
        evento = EventosRepository.create(self.evento_data)
        success = EventosRepository.delete(evento.id)
        self.assertTrue(success)
        self.assertEqual(Evento.objects.count(), 0)
