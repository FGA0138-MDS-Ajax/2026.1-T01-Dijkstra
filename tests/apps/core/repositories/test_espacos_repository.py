import uuid

from django.test import TestCase

from apps.core.models.espacos_models import EspacoFisico
from apps.core.repositories.espacos_repository import EspacosRepository

# from unittest.mock import MagicMock


class TestEspacosRepository(TestCase):
    def setUp(self):
        self.repository = EspacosRepository()

        self.data = {
            "nome": "quadra",
            "localizacao": "local teste",
            "descricao": "quadra poliesportiva",
        }

    def test_create(self):
        espaco = self.repository.create(self.data)

        self.assertEqual(
            EspacoFisico.objects.count(),
            1,
        )

        self.assertEqual(
            espaco.nome,
            self.data["nome"],
        )

    def test_get_by_id_existente(self):
        espaco = self.repository.create(self.data)

        resultado = self.repository.get_by_id(espaco.id)

        self.assertEqual(
            resultado.id,
            espaco.id,
        )

    def test_get_by_id_inexistente(self):
        resultado = self.repository.get_by_id(uuid.uuid4())

        self.assertIsNone(resultado)

    def test_get_all(self):
        self.repository.create(self.data)

        self.repository.create(
            {
                **self.data,
                "nome": "Ginásio",
            }
        )

        resultado = self.repository.get_all()

        self.assertEqual(
            len(resultado),
            2,
        )

    def test_update_existente(self):
        espaco = self.repository.create(self.data)

        atualizado = self.repository.update(
            espaco.id,
            {
                "nome": "Campo Futebol Atualizado",
            },
        )

        self.assertEqual(
            atualizado.nome,
            "Campo Futebol Atualizado",
        )

    def test_update_inexistente(self):
        resultado = self.repository.update(
            uuid.uuid4(),
            {
                "nome": "Teste",
            },
        )

        self.assertIsNone(resultado)

    def test_delete_existente(self):
        espaco = self.repository.create(self.data)

        resultado = self.repository.delete(espaco.id)

        self.assertTrue(resultado)

        self.assertEqual(
            EspacoFisico.objects.count(),
            0,
        )

    def test_delete_inexistente(self):
        resultado = self.repository.delete(uuid.uuid4())

        self.assertFalse(resultado)
