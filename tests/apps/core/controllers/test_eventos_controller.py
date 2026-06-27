import json
import uuid
from datetime import date, time
from unittest.mock import MagicMock, patch

from django.test import TestCase, Client
from django.urls import reverse

from django.contrib.auth import get_user_model

from apps.core.controllers.eventos_controller import EventosController
from apps.core.models.eventos_models import Evento
from apps.core.models.organizacoes_models import Organizacao


class EventosControllerExtraTest(TestCase):
    """Testes para o controller de Eventos."""

    def setUp(self):
        self.client = Client()
        self.organizador = get_user_model().objects.create_user(
            username="rest_org",
            password="senha123",
            tipo="OR",
            nome_completo="Organizador Teste",
        )
        self.organizacao = Organizacao.objects.create(
            nome="Organização REST", descricao="Org de teste.",
        )
        self.evento_data = {
            "nome": "Evento Teste",
            "data": "2023-10-27",
            "horario": "14:00:00",
            "local": "Local Teste",
            "organizador_id": str(self.organizador.id),
            "organizacao_id": str(self.organizacao.id),
            "descricao": "Descrição Teste",
            "capacidade": 100,
        }
        self.evento = Evento.objects.create(
            nome="Existente",
            data=date(2023, 10, 27),
            horario=time(14, 0),
            local="Local",
            organizador=self.organizador,
            organizacao=self.organizacao,
            descricao="Desc",
            capacidade=50,
        )

    def test_create_evento(self):
        response = self.client.post(
            reverse("eventos-list"),
            data=json.dumps(self.evento_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertEqual(data["nome"], "Evento Teste")

    def test_create_evento_multipart(self):
        """POST com multipart/form-data cria evento."""
        response = self.client.post(
            reverse("eventos-list"),
            data=self.evento_data,
        )
        self.assertEqual(response.status_code, 201)

    def test_create_evento_erro(self):
        """POST com dados inválidos retorna 400."""
        response = self.client.post(
            reverse("eventos-list"),
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_create_evento_com_imagem(self):
        """POST multipart com imagem cobre branch de FILES."""
        from django.core.files.uploadedfile import SimpleUploadedFile

        imagem = SimpleUploadedFile("foto.jpg", b"conteudo", content_type="image/jpeg")
        data = {**self.evento_data, "imagem": imagem}
        response = self.client.post(reverse("eventos-list"), data=data)
        self.assertEqual(response.status_code, 201)

    @patch("apps.core.controllers.eventos_controller.EventosService.listar_eventos_publicados")
    def test_get_json(self, mock_listar_eventos):
        evento = Evento.objects.create(
            nome="Evento JSON",
            data=date.today(),
            horario=time(10, 0),
            local="Local",
            organizador=self.organizador,
            organizacao=self.organizacao,
            capacidade=100,
        )

        mock_listar_eventos.return_value = [evento]

        response = self.client.get(
            reverse("eventos-list"),
            HTTP_ACCEPT="application/json",
        )

        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)

        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["nome"], "Evento JSON")

    def test_serialize_evento_sem_imagem(self):
        evento = Evento.objects.create(
            nome="Evento Teste",
            data=date.today(),
            horario=time(10, 0),
            local="Local",
            organizador=self.organizador,
            organizacao=self.organizacao,
            capacidade=100,
        )

        controller = EventosController()

        data = controller._serialize_evento(evento)

        self.assertEqual(data["nome"], evento.nome)
        self.assertEqual(data["local"], evento.local)
        self.assertEqual(data["organizador"], str(evento.organizador_id))
        self.assertEqual(data["organizacao"], str(evento.organizacao_id))
        self.assertEqual(data["capacidade"], evento.capacidade)
        self.assertEqual(data["imagem"], None)

    def test_serialize_evento_com_imagem(self):
        controller = EventosController()

        evento = MagicMock()
        evento.id = uuid.uuid4()
        evento.nome = "Evento"
        evento.data = date.today()
        evento.horario = time(10, 0)
        evento.local = "Local"
        evento.organizador = "Org"
        evento.descricao = "Descricao"
        evento.capacidade = 50
        evento.gestor = "Gestor"
        evento.criado_em = None
        evento.atualizado_em = None

        imagem = MagicMock()
        imagem.url = "/media/teste.png"
        evento.imagem = imagem

        data = controller._serialize_evento(evento)

        self.assertEqual(
            data["imagem"],
            "/media/teste.png",
        )

    @patch("apps.core.controllers.eventos_controller.EventosService.buscar_evento")
    def test_detalhes_evento(self, mock_buscar_evento):
        evento = Evento.objects.create(
            nome="Evento Detalhe",
            data=date.today(),
            horario=time(10, 0),
            local="Local",
            organizador=self.organizador,
            organizacao=self.organizacao,
            capacidade=100,
        )

        mock_buscar_evento.return_value = evento

        response = self.client.get(
            reverse(
                "detalhes_evento",
                kwargs={"evento_id": evento.id},
            )
        )

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(
            response,
            "core/detalhes_evento.html",
        )

        self.assertEqual(
            response.context["evento"],
            evento,
        )


class EventosControllerCoverageTest(TestCase):
    @patch("apps.core.controllers.eventos_controller.EventosService.listar_eventos")
    def test_get_html_response(self, mock_listar):
        mock_listar.return_value = [MagicMock(nome="Evento")]

        response = self.client.get(
            reverse("eventos-list"),
            HTTP_ACCEPT="text/html",
        )

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(
            response,
            "core/event_list.html",
        )

    @patch(
        "apps.core.controllers.eventos_controller.EventosService.get_filtered_events"
    )
    def test_event_list_controller_com_datas_validas(
        self,
        mock_filtered,
    ):
        mock_filtered.return_value = list(range(10))

        response = self.client.get(
            reverse("eventos-filtro"),
            {
                "data_inicio": "2026-01-01",
                "data_fim": "2026-12-31",
            },
        )

        self.assertEqual(response.status_code, 200)

        mock_filtered.assert_called_once_with(
            data_inicio=response.context["form"].cleaned_data["data_inicio"],
            data_fim=response.context["form"].cleaned_data["data_fim"],
        )

    @patch(
        "apps.core.controllers.eventos_controller.EventosService.get_filtered_events"
    )
    def test_event_list_controller_com_paginacao(
        self,
        mock_filtered,
    ):
        mock_filtered.return_value = list(range(20))

        response = self.client.get(
            reverse("eventos-filtro"),
            {"page": 2},
        )

        self.assertEqual(response.status_code, 200)

        self.assertIn(
            "page_obj",
            response.context,
        )

        self.assertEqual(
            response.context["page_obj"].number,
            2,
        )
