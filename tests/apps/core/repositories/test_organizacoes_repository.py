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


class VinculoMembroRepositoryTest(TestCase):
    def setUp(self):
        self.repository = OrganizacoesRepository()

    @patch(
        "apps.core.repositories.organizacoes_repository.UsuarioOrganizacao.objects.filter"
    )
    def test_listar_membros(self, mock_filter):
        membro = MagicMock()
        mock_filter.return_value.select_related.return_value = [membro]

        result = self.repository.listar_membros("org-id")

        mock_filter.assert_called_once_with(organizacao_id="org-id")
        self.assertEqual(result, [membro])

    @patch(
        "apps.core.repositories.organizacoes_repository.UsuarioOrganizacao.objects.get_or_create"
    )
    def test_adicionar_membro_novo(self, mock_get_or_create):
        vinculo = MagicMock()
        mock_get_or_create.return_value = (vinculo, True)

        result = self.repository.adicionar_membro("org-id", "usr-id")

        mock_get_or_create.assert_called_once_with(
            organizacao_id="org-id",
            usuario_id="usr-id",
        )
        self.assertEqual(result, vinculo)

    @patch(
        "apps.core.repositories.organizacoes_repository.UsuarioOrganizacao.objects.get_or_create"
    )
    def test_adicionar_membro_ja_existente_nao_duplica(self, mock_get_or_create):
        vinculo = MagicMock()
        mock_get_or_create.return_value = (vinculo, False)

        result = self.repository.adicionar_membro("org-id", "usr-id")

        self.assertEqual(result, vinculo)
        mock_get_or_create.assert_called_once()

    @patch(
        "apps.core.repositories.organizacoes_repository.UsuarioOrganizacao.objects.filter"
    )
    def test_remover_membro_existente(self, mock_filter):
        mock_filter.return_value.delete.return_value = (1, {})

        result = self.repository.remover_membro("org-id", "usr-id")

        mock_filter.assert_called_once_with(
            organizacao_id="org-id",
            usuario_id="usr-id",
        )
        self.assertTrue(result)

    @patch(
        "apps.core.repositories.organizacoes_repository.UsuarioOrganizacao.objects.filter"
    )
    def test_remover_membro_inexistente(self, mock_filter):
        mock_filter.return_value.delete.return_value = (0, {})

        result = self.repository.remover_membro("org-id", "usr-id")

        self.assertFalse(result)

    @patch("apps.core.repositories.organizacoes_repository.Usuario.objects.exclude")
    @patch(
        "apps.core.repositories.organizacoes_repository.UsuarioOrganizacao.objects.filter"
    )
    def test_listar_usuarios_sem_vinculo(self, mock_filter, mock_exclude):
        usuario = MagicMock()
        mock_filter.return_value.values_list.return_value = ["usr-1"]
        mock_exclude.return_value.filter.return_value.order_by.return_value = [usuario]

        result = self.repository.listar_usuarios_sem_vinculo("org-id")

        mock_filter.assert_called_once_with(organizacao_id="org-id")
        mock_exclude.assert_called_once_with(id__in=["usr-1"])
        self.assertEqual(result, [usuario])

    @patch("apps.core.repositories.organizacoes_repository.Organizacao.objects.filter")
    @patch(
        "apps.core.repositories.organizacoes_repository.UsuarioOrganizacao.objects.filter"
    )
    def test_listar_organizacoes_do_usuario(self, mock_vinculo_filter, mock_org_filter):
        org = MagicMock()
        mock_vinculo_filter.return_value.values_list.return_value = ["org-1"]
        mock_org_filter.return_value.filter.return_value = [org]

        result = self.repository.listar_organizacoes_do_usuario("usr-id")

        mock_vinculo_filter.assert_called_once_with(usuario_id="usr-id")
        self.assertEqual(result, [org])
