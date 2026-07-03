from uuid import uuid4

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.core.models.organizacoes_models import Organizacao, UsuarioOrganizacao


class OrganizacoesControllerTest(TestCase):
    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            username="tester",
            password="12345678",
            tipo="GE",
        )

        self.client.force_login(self.user)

        self.organizacao = Organizacao.objects.create(
            nome="Atlética FGA",
            descricao="Organização esportiva universitária",
        )

    def test_organizacao_nova_get(self):
        response = self.client.get(reverse("organizacao-nova"))

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_organizacao_nova_post_valido(self):
        quantidade_antes = Organizacao.objects.count()

        response = self.client.post(
            reverse("organizacao-nova"),
            {
                "nome": "Centro Olímpico Universitário",
                "descricao": "Nova organização",
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertEqual(
            Organizacao.objects.count(),
            quantidade_antes + 1,
        )

    def test_organizacao_detalhe(self):
        response = self.client.get(
            reverse(
                "organizacao-detalhe",
                args=[self.organizacao.id],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_organizacao_detalhe_inexistente(self):
        response = self.client.get(
            reverse(
                "organizacao-detalhe",
                args=[uuid4()],
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_organizacao_editar_get(self):
        response = self.client.get(
            reverse(
                "organizacao-editar",
                args=[self.organizacao.id],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_organizacao_editar_post(self):
        response = self.client.post(
            reverse(
                "organizacao-editar",
                args=[self.organizacao.id],
            ),
            {
                "nome": "Atlética Atualizada",
                "descricao": "Descrição atualizada",
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.organizacao.refresh_from_db()

        self.assertEqual(
            self.organizacao.nome,
            "Atlética Atualizada",
        )

    def test_organizacao_deletar_get_nao_permitido(self):
        """Exclusão é POST-only (confirmação ocorre em modal no front)."""
        response = self.client.get(
            reverse(
                "organizacao-deletar",
                args=[self.organizacao.id],
            )
        )

        self.assertEqual(
            response.status_code,
            405,
        )

    def test_organizacao_deletar_post(self):
        response = self.client.post(
            reverse(
                "organizacao-deletar",
                args=[self.organizacao.id],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertFalse(Organizacao.objects.filter(id=self.organizacao.id).exists())

    def test_organizacoes_list(self):
        response = self.client.get(
            reverse("organizacoes-list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "core/organizacoes/list.html",
        )

        self.assertIn(
            "organizacoes",
            response.context,
        )


class MembrosControllerTest(TestCase):
    def setUp(self):
        User = get_user_model()

        self.gestor = User.objects.create_user(
            username="gestor",
            password="12345678",
            tipo="GE",
        )
        self.organizador = User.objects.create_user(
            username="organizador",
            password="12345678",
            tipo="OR",
        )
        self.aluno = User.objects.create_user(
            username="aluno",
            password="12345678",
            tipo="AL",
        )
        self.organizacao = Organizacao.objects.create(
            nome="Atlética FGA",
            descricao="Organização esportiva universitária",
        )
        self.client.force_login(self.gestor)

    # --- membros_list (GET) ---

    def test_membros_list_retorna_200(self):
        response = self.client.get(
            reverse("organizacao-membros", args=[self.organizacao.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_membros_list_usa_template_correto(self):
        response = self.client.get(
            reverse("organizacao-membros", args=[self.organizacao.id])
        )
        self.assertTemplateUsed(response, "core/organizacoes/membros.html")

    def test_membros_list_contexto_tem_organizacao(self):
        response = self.client.get(
            reverse("organizacao-membros", args=[self.organizacao.id])
        )
        self.assertEqual(response.context["organizacao"], self.organizacao)

    def test_membros_list_contexto_tem_membros_e_disponiveis(self):
        response = self.client.get(
            reverse("organizacao-membros", args=[self.organizacao.id])
        )
        self.assertIn("membros", response.context)
        self.assertIn("disponiveis", response.context)

    def test_membros_list_organizacao_inexistente_retorna_404(self):
        response = self.client.get(
            reverse("organizacao-membros", args=[uuid4()])
        )
        self.assertEqual(response.status_code, 404)

    def test_membros_list_sem_autenticacao_redireciona(self):
        self.client.logout()
        response = self.client.get(
            reverse("organizacao-membros", args=[self.organizacao.id])
        )
        self.assertEqual(response.status_code, 302)

    def test_membros_list_acesso_negado_para_nao_gestor(self):
        self.client.force_login(self.aluno)
        response = self.client.get(
            reverse("organizacao-membros", args=[self.organizacao.id])
        )
        self.assertEqual(response.status_code, 302)

    # --- adicionar_membro (POST) ---

    def test_adicionar_membro_cria_vinculo(self):
        response = self.client.post(
            reverse("organizacao-adicionar-membro", args=[self.organizacao.id]),
            {"usuario_id": str(self.organizador.id)},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            UsuarioOrganizacao.objects.filter(
                organizacao=self.organizacao,
                usuario=self.organizador,
            ).exists()
        )

    def test_adicionar_membro_redireciona_para_membros(self):
        response = self.client.post(
            reverse("organizacao-adicionar-membro", args=[self.organizacao.id]),
            {"usuario_id": str(self.organizador.id)},
        )
        self.assertRedirects(
            response,
            reverse("organizacao-membros", args=[self.organizacao.id]),
        )

    def test_adicionar_membro_sem_usuario_id_nao_cria_vinculo(self):
        response = self.client.post(
            reverse("organizacao-adicionar-membro", args=[self.organizacao.id]),
            {},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(UsuarioOrganizacao.objects.count(), 0)

    def test_adicionar_membro_duplicado_nao_cria_segundo_vinculo(self):
        UsuarioOrganizacao.objects.create(
            organizacao=self.organizacao,
            usuario=self.organizador,
        )
        self.client.post(
            reverse("organizacao-adicionar-membro", args=[self.organizacao.id]),
            {"usuario_id": str(self.organizador.id)},
        )
        self.assertEqual(UsuarioOrganizacao.objects.count(), 1)

    def test_adicionar_membro_sem_autenticacao_redireciona(self):
        self.client.logout()
        response = self.client.post(
            reverse("organizacao-adicionar-membro", args=[self.organizacao.id]),
            {"usuario_id": str(self.organizador.id)},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(UsuarioOrganizacao.objects.count(), 0)

    def test_adicionar_membro_acesso_negado_para_nao_gestor(self):
        self.client.force_login(self.aluno)
        response = self.client.post(
            reverse("organizacao-adicionar-membro", args=[self.organizacao.id]),
            {"usuario_id": str(self.organizador.id)},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(UsuarioOrganizacao.objects.count(), 0)

    # --- remover_membro (POST) ---

    def test_remover_membro_exclui_vinculo(self):
        UsuarioOrganizacao.objects.create(
            organizacao=self.organizacao,
            usuario=self.organizador,
        )
        response = self.client.post(
            reverse(
                "organizacao-remover-membro",
                args=[self.organizacao.id, self.organizador.id],
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            UsuarioOrganizacao.objects.filter(
                organizacao=self.organizacao,
                usuario=self.organizador,
            ).exists()
        )

    def test_remover_membro_redireciona_para_membros(self):
        UsuarioOrganizacao.objects.create(
            organizacao=self.organizacao,
            usuario=self.organizador,
        )
        response = self.client.post(
            reverse(
                "organizacao-remover-membro",
                args=[self.organizacao.id, self.organizador.id],
            )
        )
        self.assertRedirects(
            response,
            reverse("organizacao-membros", args=[self.organizacao.id]),
        )

    def test_remover_membro_sem_vinculo_nao_levanta_excecao(self):
        response = self.client.post(
            reverse(
                "organizacao-remover-membro",
                args=[self.organizacao.id, self.organizador.id],
            )
        )
        self.assertEqual(response.status_code, 302)

    def test_remover_membro_sem_autenticacao_redireciona(self):
        self.client.logout()
        UsuarioOrganizacao.objects.create(
            organizacao=self.organizacao,
            usuario=self.organizador,
        )
        response = self.client.post(
            reverse(
                "organizacao-remover-membro",
                args=[self.organizacao.id, self.organizador.id],
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(UsuarioOrganizacao.objects.count(), 1)

    def test_remover_membro_acesso_negado_para_nao_gestor(self):
        self.client.force_login(self.aluno)
        UsuarioOrganizacao.objects.create(
            organizacao=self.organizacao,
            usuario=self.organizador,
        )
        response = self.client.post(
            reverse(
                "organizacao-remover-membro",
                args=[self.organizacao.id, self.organizador.id],
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(UsuarioOrganizacao.objects.count(), 1)
