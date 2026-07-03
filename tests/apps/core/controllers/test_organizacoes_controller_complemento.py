from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.core.models.organizacoes_models import Organizacao

User = get_user_model()


class OrganizacoesControllerComplementoTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            username="tester_complemento",
            password="12345678",
            tipo="GE",
        )

        self.organizacao = Organizacao.objects.create(
            nome="Atlética Complemento",
            descricao="Organização esportiva universitária",
        )

    def test_organizacoes_list_sem_autenticacao(self):
        """Cobre o ramo 'else: org.e_minha = False' para usuário anônimo."""
        response = self.client.get(reverse("organizacoes-list"))

        self.assertEqual(response.status_code, 200)
        organizacoes = list(response.context["organizacoes"])
        self.assertTrue(all(org.e_minha is False for org in organizacoes))

    def test_organizacao_nova_post_invalido(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("organizacao-nova"), {})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/organizacoes/form.html")
        self.assertTrue(response.context["form"].errors)

    def test_organizacao_editar_acesso_negado_para_aluno(self):
        """Cobre 'raise PermissionDenied()' do decorator gestor_ou_organizacao."""
        aluno = User.objects.create_user(
            username="aluno_complemento",
            password="12345678",
            tipo="AL",
        )
        self.client.force_login(aluno)

        response = self.client.get(
            reverse(
                "organizacao-editar",
                kwargs={"organizacao_id": self.organizacao.id},
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_organizacao_editar_post_invalido(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "organizacao-editar",
                kwargs={"organizacao_id": self.organizacao.id},
            ),
            {},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/organizacoes/form.html")
        self.assertTrue(response.context["form"].errors)

        self.organizacao.refresh_from_db()
        self.assertEqual(self.organizacao.nome, "Atlética Complemento")
