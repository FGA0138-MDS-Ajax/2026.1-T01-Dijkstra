from unittest.mock import patch
import uuid

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.core.models.espacos_models import EspacoFisico

User = get_user_model()


class EspacosControllerTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            username="tester",
            password="12345678",
            tipo="GE",
        )

        self.client.force_login(self.user)

        self.espaco = EspacoFisico.objects.create(
            nome="Quadra Central",
            localizacao="Campus Darcy Ribeiro",
            descricao="Quadra poliesportiva",
            status=EspacoFisico.Status.DISPONIVEL,
        )

        self.form_data = {
            "nome": "Ginásio Principal",
            "localizacao": "Bloco A",
            "descricao": "Ginásio coberto",
            "status": EspacoFisico.Status.DISPONIVEL,
        }

    @patch("apps.core.controllers.espacos_controller._service.listar_espacos")
    def test_espacos_list(self, mock_listar):
        mock_listar.return_value = [self.espaco]

        response = self.client.get(reverse("espacos-list"))

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "core/espacos/list.html",
        )

        self.assertIn(
            "espacos",
            response.context,
        )

        mock_listar.assert_called_once()

    def test_espaco_novo_get(self):
        response = self.client.get(reverse("espaco-novo"))

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "core/espacos/form.html",
        )

        self.assertEqual(
            response.context["acao"],
            "Criar",
        )

    def test_espaco_novo_post_valido(self):
        quantidade_antes = EspacoFisico.objects.count()

        response = self.client.post(
            reverse("espaco-novo"),
            self.form_data,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertEqual(
            EspacoFisico.objects.count(),
            quantidade_antes + 1,
        )

        novo = EspacoFisico.objects.get(nome="Ginásio Principal")

        self.assertEqual(
            novo.localizacao,
            "Bloco A",
        )

    def test_espaco_novo_post_invalido(self):
        response = self.client.post(
            reverse("espaco-novo"),
            {},
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "core/espacos/form.html",
        )

        self.assertTrue(response.context["form"].errors)

    def test_espaco_detalhe(self):
        response = self.client.get(
            reverse(
                "espaco-detalhe",
                kwargs={
                    "espaco_id": self.espaco.id,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "core/espacos/detalhe.html",
        )

        self.assertEqual(
            response.context["espaco"].id,
            self.espaco.id,
        )

    def test_espaco_detalhe_404(self):
        response = self.client.get(
            reverse(
                "espaco-detalhe",
                kwargs={
                    "espaco_id": uuid.uuid4(),
                },
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
                kwargs={
                    "espaco_id": self.espaco.id,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "core/espacos/form.html",
        )

        self.assertEqual(
            response.context["acao"],
            "Editar",
        )

    def test_espaco_editar_post_valido(self):
        response = self.client.post(
            reverse(
                "espaco-editar",
                kwargs={
                    "espaco_id": self.espaco.id,
                },
            ),
            {
                "nome": "Quadra Atualizada",
                "localizacao": "Novo Local",
                "descricao": "Nova Descrição",
                "status": EspacoFisico.Status.EM_MANUTENCAO,
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

        self.assertEqual(
            self.espaco.status,
            EspacoFisico.Status.EM_MANUTENCAO,
        )

    def test_espaco_editar_post_invalido(self):
        response = self.client.post(
            reverse(
                "espaco-editar",
                kwargs={
                    "espaco_id": self.espaco.id,
                },
            ),
            {},
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "core/espacos/form.html",
        )

    def test_espaco_editar_404(self):
        response = self.client.get(
            reverse(
                "espaco-editar",
                kwargs={
                    "espaco_id": uuid.uuid4(),
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_espaco_deletar_get(self):
        response = self.client.get(
            reverse(
                "espaco-deletar",
                kwargs={
                    "espaco_id": self.espaco.id,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "core/espacos/confirmar_deletar.html",
        )

    def test_espaco_deletar_post(self):
        espaco_id = self.espaco.id

        response = self.client.post(
            reverse(
                "espaco-deletar",
                kwargs={
                    "espaco_id": espaco_id,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertFalse(EspacoFisico.objects.filter(id=espaco_id).exists())

    def test_espaco_deletar_404(self):
        response = self.client.get(
            reverse(
                "espaco-deletar",
                kwargs={
                    "espaco_id": uuid.uuid4(),
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )
