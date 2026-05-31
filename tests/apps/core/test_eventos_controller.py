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
        response = self.client.get(reverse("eventos-list"))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) >= 1)

    def test_get_evento_detail(self):
        response = self.client.get(
            reverse("eventos-detail", kwargs={"evento_id": self.evento.id})
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["nome"], "Existente")

    def test_create_evento(self):
        response = self.client.post(
            reverse("eventos-list"),
            data=json.dumps(self.evento_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertEqual(data["nome"], "Evento Teste")

    def test_update_evento(self):
        update_data = {"nome": "Novo Nome"}
        response = self.client.put(
            reverse("eventos-detail", kwargs={"evento_id": self.evento.id}),
            data=json.dumps(update_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.evento.refresh_from_db()
        self.assertEqual(self.evento.nome, "Novo Nome")

    def test_delete_evento(self):
        response = self.client.delete(
            reverse("eventos-detail", kwargs={"evento_id": self.evento.id})
        )
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Evento.objects.filter(id=self.evento.id).exists())

    # -------------------------------------------------------------------------------
    def test_get_evento_nao_encontrado(self):
        """GET com id inexistente retorna 404."""
        response = self.client.get(
            reverse("eventos-detail", kwargs={"evento_id": 99999})
        )
        self.assertEqual(response.status_code, 404)

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

    def test_update_evento_nao_encontrado(self):
        """PUT com id inexistente retorna 404."""
        response = self.client.put(
            reverse("eventos-detail", kwargs={"evento_id": 99999}),
            data=json.dumps({"nome": "Novo"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_update_evento_erro(self):
        """PUT com JSON inválido retorna 400."""
        response = self.client.put(
            reverse("eventos-detail", kwargs={"evento_id": self.evento.id}),
            data="json invalido",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_serialize_imagem_none(self):
        """Evento sem imagem retorna imagem como None na serialização."""
        response = self.client.get(
            reverse("eventos-detail", kwargs={"evento_id": self.evento.id})
        )
        data = json.loads(response.content)
        self.assertIsNone(data["imagem"])

    def test_create_evento_com_imagem(self):
        """POST multipart com imagem cobre branch de FILES."""
        from django.core.files.uploadedfile import SimpleUploadedFile

        imagem = SimpleUploadedFile("foto.jpg", b"conteudo", content_type="image/jpeg")
        data = {**self.evento_data, "imagem": imagem}
        response = self.client.post(reverse("eventos-list"), data=data)
        self.assertEqual(response.status_code, 201)

    def test_delete_evento_nao_encontrado(self):
        """DELETE com id inexistente retorna 404."""
        response = self.client.delete(
            reverse("eventos-detail", kwargs={"evento_id": 99999})
        )
        self.assertEqual(response.status_code, 404)

    # -------------------------------------------------------------------------------
