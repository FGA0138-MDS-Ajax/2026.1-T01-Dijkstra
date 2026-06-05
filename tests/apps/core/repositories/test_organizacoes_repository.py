# # test_organizacoes_repository.py

# from django.test import TestCase

# from apps.core.models.organizacoes_models import Organizacao
# from apps.core.repositories.organizacoes_repository import OrganizacoesRepository


# class OrganizacoesRepositoryTest(TestCase):
#     def setUp(self):
#         self.repository = OrganizacoesRepository()

#         self.data = {
#             "nome": "Quadra Central",
#             "localizacao": "Campus",
#             "descricao": "Quadra esportiva",
#         }

#     def test_create(self):
#         espaco = self.repository.create(self.data)

#         self.assertEqual(espaco.nome, "Quadra Central")
#         self.assertEqual(Organizacao.objects.count(), 1)

#     def test_get_by_id(self):
#         espaco = self.repository.create(self.data)

#         encontrado = self.repository.get_by_id(espaco.id)

#         self.assertEqual(encontrado.id, espaco.id)

#     def test_get_by_id_inexistente(self):
#         self.assertIsNone(
#             self.repository.get_by_id("00000000-0000-0000-0000-000000000000")
#         )

#     def test_get_all(self):
#         self.repository.create(self.data)
#         self.repository.create({**self.data, "nome": "Ginásio"})

#         self.assertEqual(len(self.repository.get_all()), 2)

#     def test_update(self):
#         espaco = self.repository.create(self.data)

#         atualizado = self.repository.update(espaco.id, {"nome": "Novo Nome"})

#         self.assertEqual(atualizado.nome, "Novo Nome")

#     def test_update_inexistente(self):
#         self.assertIsNone(
#             self.repository.update(
#                 "00000000-0000-0000-0000-000000000000", {"nome": "X"}
#             )
#         )

#     def test_delete(self):
#         espaco = self.repository.create(self.data)

#         self.assertTrue(self.repository.delete(espaco.id))

#         self.assertEqual(Organizacao.objects.count(), 0)

#     def test_delete_inexistente(self):
#         self.assertFalse(self.repository.delete("00000000-0000-0000-0000-000000000000"))
from unittest.mock import MagicMock, patch

from django.test import TestCase

from apps.core.repositories.organizacoes_repository import (
    OrganizacoesRepository,
)


class OrganizacoesRepositoryTest(TestCase):
    def setUp(self):
        self.repository = OrganizacoesRepository()

    @patch("apps.core.repositories.organizacoes_repository.Organizacao.objects.create")
    def test_create(self, mock_create):
        obj = MagicMock()

        mock_create.return_value = obj

        result = self.repository.create({"nome": "Teste"})

        self.assertEqual(result, obj)

        mock_create.assert_called_once_with(nome="Teste")

    @patch("apps.core.repositories.organizacoes_repository.Organizacao.objects.get")
    def test_get_by_id_sucesso(self, mock_get):
        obj = MagicMock()

        mock_get.return_value = obj

        result = self.repository.get_by_id("id")

        self.assertEqual(result, obj)

    @patch("apps.core.repositories.organizacoes_repository.Organizacao.objects.get")
    def test_get_by_id_nao_encontrado(self, mock_get):
        from apps.core.models.organizacoes_models import (
            Organizacao,
        )

        mock_get.side_effect = Organizacao.DoesNotExist

        result = self.repository.get_by_id("id")

        self.assertIsNone(result)

    @patch("apps.core.repositories.organizacoes_repository.Organizacao.objects.all")
    def test_get_all(self, mock_all):
        objs = [MagicMock(), MagicMock()]

        mock_all.return_value = objs

        result = self.repository.get_all()

        self.assertEqual(result, objs)

    @patch.object(
        OrganizacoesRepository,
        "get_by_id",
    )
    def test_update_sucesso(self, mock_get):
        obj = MagicMock()

        mock_get.return_value = obj

        result = self.repository.update(
            "id",
            {
                "nome": "Novo Nome",
                "sigla": "ABC",
            },
        )

        self.assertEqual(result, obj)

        self.assertEqual(
            obj.nome,
            "Novo Nome",
        )

        self.assertEqual(
            obj.sigla,
            "ABC",
        )

        obj.save.assert_called_once()

    @patch.object(
        OrganizacoesRepository,
        "get_by_id",
    )
    def test_update_nao_encontrado(
        self,
        mock_get,
    ):
        mock_get.return_value = None

        result = self.repository.update(
            "id",
            {"nome": "Novo"},
        )

        self.assertIsNone(result)

    @patch.object(
        OrganizacoesRepository,
        "get_by_id",
    )
    def test_delete_sucesso(self, mock_get):
        obj = MagicMock()

        mock_get.return_value = obj

        result = self.repository.delete("id")

        self.assertTrue(result)

        obj.delete.assert_called_once()

    @patch.object(
        OrganizacoesRepository,
        "get_by_id",
    )
    def test_delete_nao_encontrado(
        self,
        mock_get,
    ):
        mock_get.return_value = None

        result = self.repository.delete("id")

        self.assertFalse(result)
