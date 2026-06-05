from unittest.mock import MagicMock

from django.test import TestCase

from apps.core.repositories.espacos_repository import EspacosRepository
from apps.core.services.espacos_service import EspacosService


class TestEspacosService(TestCase):
    def setUp(self):
        self.repository_mock = MagicMock(spec=EspacosRepository)
        self.service = EspacosService(repository=self.repository_mock)

    def test_criar_espaco(self):
        data = {
            "nome": "Quadra",
            "localizacao": "Quada",
            "descricao": "Quadra Poliesportiva",
        }

        self.service.criar_espaco(data)

        self.repository_mock.create.assert_called_once_with(data)

    def test_criar_espaco_sem_nome(self):
        with self.assertRaises(ValueError):
            self.service.criar_espaco(
                {
                    "localizacao": "Quadra Teste",
                    "descricao": "Teste",
                }
            )

    def test_listar_espacos(self):
        self.service.listar_espacos()

        self.repository_mock.get_all.assert_called_once()

    def test_obter_espaco(self):
        self.service.obter_espaco("abc")

        self.repository_mock.get_by_id.assert_called_once_with("abc")

    def test_atualizar_espaco(self):
        data = {
            "nome": "Novo Nome",
        }

        self.service.atualizar_espaco(
            "abc",
            data,
        )

        self.repository_mock.update.assert_called_once_with(
            "abc",
            data,
        )

    def test_remover_espaco(self):
        self.service.remover_espaco("abc")

        self.repository_mock.delete.assert_called_once_with("abc")

    def test_init_sem_repository(self):
        service = EspacosService()

        self.assertIsInstance(
            service.repository,
            EspacosRepository,
        )

