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

    # ------------------------------------------------------------------
    # Membros / vínculo
    # ------------------------------------------------------------------

    def test_listar_membros(self):
        self.repository.listar_membros.return_value = ["membro1", "membro2"]

        resultado = self.service.listar_membros("org-id")

        self.repository.listar_membros.assert_called_once_with("org-id")
        self.assertEqual(resultado, ["membro1", "membro2"])

    def test_adicionar_membro(self):
        vinculo = MagicMock()
        self.repository.adicionar_membro.return_value = vinculo

        resultado = self.service.adicionar_membro("org-id", "usr-id")

        self.repository.adicionar_membro.assert_called_once_with("org-id", "usr-id")
        self.assertEqual(resultado, vinculo)

    def test_remover_membro_sucesso(self):
        self.repository.remover_membro.return_value = True

        resultado = self.service.remover_membro("org-id", "usr-id")

        self.repository.remover_membro.assert_called_once_with("org-id", "usr-id")
        self.assertTrue(resultado)

    def test_remover_membro_inexistente(self):
        self.repository.remover_membro.return_value = False

        resultado = self.service.remover_membro("org-id", "usr-id")

        self.assertFalse(resultado)

    def test_listar_usuarios_sem_vinculo(self):
        self.repository.listar_usuarios_sem_vinculo.return_value = ["usr1"]

        resultado = self.service.listar_usuarios_sem_vinculo("org-id")

        self.repository.listar_usuarios_sem_vinculo.assert_called_once_with("org-id")
        self.assertEqual(resultado, ["usr1"])

    def test_listar_organizacoes_do_usuario(self):
        self.repository.listar_organizacoes_do_usuario.return_value = ["org1"]

        resultado = self.service.listar_organizacoes_do_usuario("usr-id")

        self.repository.listar_organizacoes_do_usuario.assert_called_once_with("usr-id")
        self.assertEqual(resultado, ["org1"])
