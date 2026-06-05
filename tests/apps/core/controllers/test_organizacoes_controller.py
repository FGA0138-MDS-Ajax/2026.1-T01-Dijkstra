from uuid import uuid4

from django.test import TestCase
from django.urls import reverse

from apps.core.models.organizacoes_models import Organizacao


class OrganizacoesControllerTest(TestCase):
    def setUp(self):
        self.organizacao = Organizacao.objects.create(
            nome="Atlética FGA",
            descricao="Organização esportiva universitária",
        )

    def test_organizacoes_list(self):
        response = self.client.get(reverse("organizacoes-list"))

        self.assertEqual(
            response.status_code,
            200,
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

    def test_organizacao_deletar_get(self):
        response = self.client.get(
            reverse(
                "organizacao-deletar",
                args=[self.organizacao.id],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
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
