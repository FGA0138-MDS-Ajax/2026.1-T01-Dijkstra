from datetime import date, time

from django.test import TestCase
from django.urls import reverse

from apps.core.models.eventos_models import Evento


class CrudEventosControllerTest(TestCase):
    def setUp(self):
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

    def test_gestao_eventos_list_com_filtro_status(self):
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

        self.assertTemplateUsed(
            response,
            "core/eventos/list.html",
        )

        self.assertEqual(
            response.context["status_filtro"],
            Evento.Status.PUBLICADO,
        )

        # eventos = list(response.context["eventos"])

        # self.assertEqual(len(eventos), 1)
        # self.assertEqual(
        #     eventos[0].nome,
        #     "Evento Teste",
        # )

        eventos = response.context["eventos"]

        self.assertTrue(eventos.exists())

        for evento in eventos:
            self.assertEqual(
                evento.status,
                Evento.Status.PUBLICADO,
            )

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
                "descricao": "Campionato de Magic",
                "capacidade": 100,
                "status": Evento.Status.PUBLICADO,
            },
        )

        self.assertEqual(response.status_code, 302)

        self.assertTrue(Evento.objects.filter(nome="Novo Evento").exists())

    def test_gestao_evento_novo_post_invalido(self):
        response = self.client.post(reverse("gestao-evento-novo"), {})

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(
            response,
            "core/eventos/form.html",
        )

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

        self.assertEqual(response.status_code, 302)

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

        self.assertEqual(response.status_code, 302)

        self.assertFalse(Evento.objects.filter(id=evento_id).exists())

    def test_gestao_eventos_list_com_filtro_status_v2(self):
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

        self.assertTemplateUsed(
            response,
            "core/eventos/list.html",
        )

        self.assertEqual(
            response.context["status_filtro"],
            Evento.Status.PUBLICADO,
        )

        self.assertFalse(
            response.context["eventos"].exclude(status=Evento.Status.PUBLICADO).exists()
        )
