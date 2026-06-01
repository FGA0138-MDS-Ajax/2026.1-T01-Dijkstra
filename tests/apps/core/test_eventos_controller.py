import json

from datetime import date, time

from django.test import TestCase, Client
from django.urls import reverse

from apps.core.models.eventos_models import Evento


class EventosControllerTest(TestCase):
    """Testes para o controller de Eventos."""

    def setUp(self):
        self.client = Client()
        self.evento_data = {
            "nome": "Evento Teste",
            "data": "2023-10-27",
            "horario": "14:00:00",
            "local": "Local Teste",
            "organizador": "Organizador Teste",
            "gestor": "Gestor Teste",
            "descricao": "Descrição Teste",
            "capacidade": 100,
        }
        self.evento = Evento.objects.create(
            nome="Existente",
            data=date(2023, 10, 27),
            horario=time(14, 0),
            local="Local",
            organizador="Org",
            gestor="Gestor",
            descricao="Desc",
            capacidade=50,
        )

    def test_list_eventos(self):
        response = self.client.get(
            reverse("eventos-list"), HTTP_ACCEPT="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) >= 1)

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
