from uuid import uuid4

from django.test import TestCase
from django.urls import reverse

from apps.core.models.espacos_models import EspacoFisico


class EspacosControllerTest(TestCase):

    def setUp(self):
        self.espaco = EspacoFisico.objects.create(
            nome="Quadra Central",
            localizacao="Campus Darcy Ribeiro",
            descricao="Quadra poliesportiva",
        )

    def test_espacos_list(self):
        response = self.client.get(
            reverse("espacos-list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_espaco_novo_get(self):
        response = self.client.get(
            reverse("espaco-novo")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_espaco_novo_post_valido(self):
        quantidade_antes = EspacoFisico.objects.count()

        response = self.client.post(
            reverse("espaco-novo"),
            {
                "nome": "Ginásio Novo",
                "localizacao": "Campus Gama",
                "descricao": "Novo espaço",
                "status": EspacoFisico.Status.DISPONIVEL,
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertEqual(
            EspacoFisico.objects.count(),
            quantidade_antes + 1,
        )

    def test_espaco_detalhe(self):
        response = self.client.get(
            reverse(
                "espaco-detalhe",
                args=[self.espaco.id],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_espaco_detalhe_inexistente(self):
        response = self.client.get(
            reverse(
                "espaco-detalhe",
                args=[uuid4()],
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_espaco_editar_get(self):
        response = self.client.get(
            reverse(
                "espaco-editar",
                args=[self.espaco.id],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_espaco_editar_post(self):
        response = self.client.post(
            reverse(
                "espaco-editar",
                args=[self.espaco.id],
            ),
            {
                "nome": "Quadra Atualizada",
                "localizacao": self.espaco.localizacao,
                "descricao": self.espaco.descricao,
                "status": EspacoFisico.Status.DISPONIVEL,
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.espaco.refresh_from_db()

        self.assertEqual(
            self.espaco.nome,
            "Quadra Atualizada",
        )

    def test_espaco_deletar_get(self):
        response = self.client.get(
            reverse(
                "espaco-deletar",
                args=[self.espaco.id],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_espaco_deletar_post(self):
        response = self.client.post(
            reverse(
                "espaco-deletar",
                args=[self.espaco.id],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertFalse(
            EspacoFisico.objects.filter(
                id=self.espaco.id
            ).exists()
        )