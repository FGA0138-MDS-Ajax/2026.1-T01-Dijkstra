from unittest.mock import MagicMock

from django.test import TestCase

from apps.core.services.organizacoes_service import (
    OrganizacoesService,
)


class OrganizacoesServiceTest(TestCase):
    def setUp(self):
        self.repository = MagicMock()

        self.service = OrganizacoesService(repository=self.repository)

    def test_criar_organizacao(self):
        obj = MagicMock()

        self.repository.create.return_value = obj

        resultado = self.service.criar_organizacao({"nome": "Teste"})

        self.assertEqual(resultado, obj)

    def test_criar_organizacao_sem_nome(self):
        with self.assertRaises(ValueError):
            self.service.criar_organizacao({})

    def test_listar_organizacoes(self):
        self.repository.get_all.return_value = ["a"]

        resultado = self.service.listar_organizacoes()

        self.assertEqual(resultado, ["a"])

    def test_obter_organizacao(self):
        obj = MagicMock()

        self.repository.get_by_id.return_value = obj

        resultado = self.service.obter_organizacao("id")

        self.assertEqual(resultado, obj)

    def test_atualizar_organizacao(self):
        obj = MagicMock()

        self.repository.update.return_value = obj

        resultado = self.service.atualizar_organizacao(
            "id",
            {"nome": "Novo"},
        )

        self.assertEqual(resultado, obj)

    def test_remover_organizacao(self):
        self.repository.delete.return_value = True

        resultado = self.service.remover_organizacao("id")

        self.assertTrue(resultado)
