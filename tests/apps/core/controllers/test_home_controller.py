from datetime import date, time
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.core.models.eventos_models import Evento
from apps.core.models.organizacoes_models import Organizacao


class HomeControllerTest(TestCase):
    def setUp(self):
        self.organizador = get_user_model().objects.create_user(
            username="home_org", password="senha123", tipo="OR",
        )
        self.organizacao = Organizacao.objects.create(
            nome="Organização Home", descricao="Org de teste.",
        )

    @patch("apps.core.controllers.home_controller.EventosService.get_filtered_events")
    def test_home(self, mock_get_filtered_events):
        evento = Evento.objects.create(
            nome="Evento Teste",
            data=date.today(),
            horario=time(10, 0),
            local="Local",
            organizador=self.organizador,
            organizacao=self.organizacao,
            capacidade=100,
        )

        mock_get_filtered_events.return_value = [evento]

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/index.html")

    @patch("apps.core.controllers.home_controller.EventosService.get_filtered_events")
    def test_home_com_filtros(self, mock_get_filtered_events):
        evento = Evento.objects.create(
            nome="Evento Teste",
            data=date.today(),
            horario=time(10, 0),
            local="Local",
            organizador=self.organizador,
            organizacao=self.organizacao,
            capacidade=100,
        )

        mock_get_filtered_events.return_value = [evento]

        response = self.client.get(
            reverse("home"),
            {
                "q": "Evento",
                "data_inicio": "2026-01-01",
                "data_fim": "2026-12-31",
            },
        )

        self.assertEqual(response.status_code, 200)

        mock_get_filtered_events.assert_called_once_with(
            query="Evento",
            data_inicio="2026-01-01",
            data_fim="2026-12-31",
        )

    @patch("apps.core.controllers.home_controller.EventosService.get_filtered_events")
    def test_home_com_paginacao(self, mock_get_filtered_events):
        eventos = []

        for i in range(20):
            eventos.append(
                Evento.objects.create(
                    nome=f"Evento {i}",
                    data=date.today(),
                    horario=time(10, 0),
                    local="Local",
                    organizador=self.organizador,
                    organizacao=self.organizacao,
                    capacidade=100,
                )
            )

        mock_get_filtered_events.return_value = eventos

        response = self.client.get(
            reverse("home"),
            {"page": 2},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/index.html")

        eventos_page = response.context["eventos"]

        self.assertEqual(eventos_page.number, 2)
        self.assertTrue(eventos_page.has_previous())
        self.assertTrue(eventos_page.has_next())
