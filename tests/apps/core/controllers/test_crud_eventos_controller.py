from datetime import date, time
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.core.models.eventos_models import Evento


class CrudEventosControllerTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="tester",
            password="senha123",
            tipo="OR",
        )

        self.client.login(
            username="tester",
            password="senha123",
        )

        self.evento = Evento.objects.create(
            nome="Evento Teste",
            data=date.today(),
            horario=time(10, 0),
            local="Local Teste",
            organizador="Organizador",
            gestor="Gestor",
            descricao="Descricao teste",
            capacidade=100,
            status=Evento.Status.PUBLICADO,
        )

    # ------------------------------------------------------------------
    # LISTAGEM
    # ------------------------------------------------------------------

    def test_gestao_eventos_list(self):
        response = self.client.get(reverse("gestao-eventos-list"))

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(
            response,
            "core/eventos/list.html",
        )

        self.assertContains(
            response,
            "Evento Teste",
        )

        self.assertEqual(
            response.context["status_filtro"],
            "",
        )

    def test_gestao_eventos_list_filtra_por_status(self):
        Evento.objects.create(
            nome="Evento Rascunho",
            data=date.today(),
            horario=time(12, 0),
            local="Outro Local",
            organizador="Outro",
            gestor="Outro",
            descricao="Outro",
            capacidade=50,
            status=Evento.Status.RASCUNHO,
        )

        response = self.client.get(
            reverse("gestao-eventos-list"),
            {"status": Evento.Status.PUBLICADO},
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.context["status_filtro"],
            Evento.Status.PUBLICADO,
        )

        self.assertFalse(
            response.context["eventos"].exclude(status=Evento.Status.PUBLICADO).exists()
        )

    # ------------------------------------------------------------------
    # CRIAÇÃO
    # ------------------------------------------------------------------

    def test_gestao_evento_novo_get(self):
        response = self.client.get(reverse("gestao-evento-novo"))

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(
            response,
            "core/eventos/form.html",
        )

    def test_gestao_evento_novo_post_valido(self):
        response = self.client.post(
            reverse("gestao-evento-novo"),
            {
                "nome": "Novo Evento",
                "data": "2026-06-20",
                "horario": "10:00",
                "local": "Auditório",
                "organizador": "Organizador",
                "gestor": "Gestor",
                "descricao": "Campeonato de Magic",
                "capacidade": 100,
                "status": Evento.Status.PUBLICADO,
            },
        )

        self.assertRedirects(
            response,
            reverse("gestao-eventos-list"),
        )

        self.assertTrue(Evento.objects.filter(nome="Novo Evento").exists())

    def test_gestao_evento_novo_post_invalido(self):
        response = self.client.post(
            reverse("gestao-evento-novo"),
            {},
        )

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(
            response,
            "core/eventos/form.html",
        )

    # ------------------------------------------------------------------
    # DETALHE
    # ------------------------------------------------------------------

    def test_gestao_evento_detalhe(self):
        response = self.client.get(
            reverse(
                "gestao-evento-detalhe",
                kwargs={
                    "evento_id": self.evento.id,
                },
            )
        )

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(
            response,
            "core/eventos/detalhe.html",
        )

        self.assertEqual(
            response.context["evento"].id,
            self.evento.id,
        )

    def test_gestao_evento_detalhe_404(self):
        response = self.client.get(
            reverse(
                "gestao-evento-detalhe",
                kwargs={
                    "evento_id": uuid.uuid4(),
                },
            )
        )

        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------
    # EDIÇÃO
    # ------------------------------------------------------------------

    def test_gestao_evento_editar_get(self):
        response = self.client.get(
            reverse(
                "gestao-evento-editar",
                kwargs={
                    "evento_id": self.evento.id,
                },
            )
        )

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(
            response,
            "core/eventos/form.html",
        )

    def test_gestao_evento_editar_post_valido(self):
        response = self.client.post(
            reverse(
                "gestao-evento-editar",
                kwargs={
                    "evento_id": self.evento.id,
                },
            ),
            {
                "nome": "Evento Atualizado",
                "data": self.evento.data.strftime("%Y-%m-%d"),
                "horario": self.evento.horario.strftime("%H:%M"),
                "local": self.evento.local,
                "organizador": self.evento.organizador,
                "gestor": self.evento.gestor,
                "descricao": self.evento.descricao,
                "capacidade": self.evento.capacidade,
                "status": self.evento.status,
            },
        )

        self.assertRedirects(
            response,
            reverse(
                "gestao-evento-detalhe",
                kwargs={
                    "evento_id": self.evento.id,
                },
            ),
        )

        self.evento.refresh_from_db()

        self.assertEqual(
            self.evento.nome,
            "Evento Atualizado",
        )

    def test_gestao_evento_editar_post_invalido(self):
        response = self.client.post(
            reverse(
                "gestao-evento-editar",
                kwargs={
                    "evento_id": self.evento.id,
                },
            ),
            {},
        )

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(
            response,
            "core/eventos/form.html",
        )

    def test_gestao_evento_editar_404(self):
        response = self.client.get(
            reverse(
                "gestao-evento-editar",
                kwargs={
                    "evento_id": uuid.uuid4(),
                },
            )
        )

        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------
    # EXCLUSÃO
    # ------------------------------------------------------------------

    def test_gestao_evento_deletar_get(self):
        response = self.client.get(
            reverse(
                "gestao-evento-deletar",
                kwargs={
                    "evento_id": self.evento.id,
                },
            )
        )

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(
            response,
            "core/eventos/confirmar_deletar.html",
        )

    def test_gestao_evento_deletar_post(self):
        evento_id = self.evento.id

        response = self.client.post(
            reverse(
                "gestao-evento-deletar",
                kwargs={
                    "evento_id": evento_id,
                },
            )
        )

        self.assertRedirects(
            response,
            reverse("gestao-eventos-list"),
        )

        self.assertFalse(Evento.objects.filter(id=evento_id).exists())

    def test_gestao_evento_deletar_404(self):
        response = self.client.get(
            reverse(
                "gestao-evento-deletar",
                kwargs={
                    "evento_id": uuid.uuid4(),
                },
            )
        )

        self.assertEqual(response.status_code, 404)
