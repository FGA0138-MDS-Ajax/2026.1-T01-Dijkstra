"""Testes para as views do aluno em inscricoes_controller.py.

Cobre:
- inscrever_evento
- cancelar_inscricao
"""

from django.urls import reverse

from apps.core.models.inscricao_models import Inscricao
from tests.apps.core.controllers.test_inscricoes_controller import (
    BaseInscricoesTest,
)


class InscreverEventoTest(BaseInscricoesTest):
    def _url_inscrever(self, evento=None):
        evento = evento or self.evento
        return reverse("inscrever_evento", kwargs={"evento_id": evento.id})

    def setUp(self):
        super().setUp()
        # A fixture base já cria uma inscrição pendente para self.aluno;
        # removemos para testar o fluxo de nova inscrição isoladamente.
        self.inscricao_pendente.delete()

    def test_inscrever_get_apenas_redireciona(self):
        self._login_aluno()

        response = self.client.get(self._url_inscrever())

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Inscricao.objects.filter(aluno=self.aluno).count(), 0)

    def test_inscrever_post_cria_inscricao(self):
        self._login_aluno()

        response = self.client.post(self._url_inscrever(), HTTP_REFERER="/eventos/")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/eventos/")
        self.assertTrue(
            Inscricao.objects.filter(aluno=self.aluno, evento=self.evento).exists()
        )

    def test_inscrever_post_sem_referer_redireciona_home(self):
        self._login_aluno()

        response = self.client.post(self._url_inscrever())

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("home"))

    def test_inscrever_post_ja_inscrito(self):
        Inscricao.objects.create(aluno=self.aluno, evento=self.evento)
        self._login_aluno()

        response = self.client.post(self._url_inscrever())

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            Inscricao.objects.filter(aluno=self.aluno, evento=self.evento).count(), 1
        )

    def test_inscrever_post_sem_vagas(self):
        self.evento.capacidade = 1
        self.evento.save(update_fields=["capacidade"])

        outro_aluno = self._criar_outro_aluno()
        Inscricao.objects.create(aluno=outro_aluno, evento=self.evento)

        self._login_aluno()
        response = self.client.post(self._url_inscrever())

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Inscricao.objects.filter(aluno=self.aluno, evento=self.evento).exists()
        )

    def test_inscrever_post_nao_conta_canceladas_e_rejeitadas_nas_vagas(self):
        self.evento.capacidade = 1
        self.evento.save(update_fields=["capacidade"])

        outro_aluno = self._criar_outro_aluno()
        Inscricao.objects.create(
            aluno=outro_aluno, evento=self.evento, status=Inscricao.Status.CANCELADA
        )

        self._login_aluno()
        response = self.client.post(self._url_inscrever())

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Inscricao.objects.filter(aluno=self.aluno, evento=self.evento).exists()
        )

    def _criar_outro_aluno(self):
        return type(self.aluno).objects.create_user(
            username="outro_aluno",
            password="senha123",
            tipo="AL",
            nome_completo="Outro Aluno",
            matricula="333333333",
        )

    def test_inscrever_nao_autenticado_redireciona_login(self):
        response = self.client.post(self._url_inscrever())

        self.assertEqual(response.status_code, 302)


class CancelarInscricaoTest(BaseInscricoesTest):
    def _url_cancelar(self, evento=None):
        evento = evento or self.evento
        return reverse("cancelar_inscricao", kwargs={"evento_id": evento.id})

    def test_cancelar_get_apenas_redireciona(self):
        self._login_aluno()

        response = self.client.get(self._url_cancelar())

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Inscricao.objects.filter(pk=self.inscricao_pendente.pk).exists()
        )

    def test_cancelar_post_remove_inscricao(self):
        self._login_aluno()

        response = self.client.post(self._url_cancelar(), HTTP_REFERER="/eventos/")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/eventos/")
        self.assertFalse(
            Inscricao.objects.filter(pk=self.inscricao_pendente.pk).exists()
        )

    def test_cancelar_post_sem_referer_redireciona_home(self):
        self._login_aluno()

        response = self.client.post(self._url_cancelar())

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("home"))

    def test_cancelar_post_sem_inscricao_nao_falha(self):
        self.inscricao_pendente.delete()
        self._login_aluno()

        response = self.client.post(self._url_cancelar())

        self.assertEqual(response.status_code, 302)

    def test_cancelar_nao_autenticado_redireciona_login(self):
        response = self.client.post(self._url_cancelar())

        self.assertEqual(response.status_code, 302)
