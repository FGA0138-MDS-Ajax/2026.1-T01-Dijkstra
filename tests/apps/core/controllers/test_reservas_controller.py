import uuid
from datetime import date, time, timedelta

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from unittest.mock import patch

from apps.core.models.espacos_models import EspacoFisico
from apps.core.models.eventos_models import Evento
from apps.core.models.organizacoes_models import Organizacao
from apps.core.models.reservas_models import ReservaEspaco

User = get_user_model()


class ReservasControllerTestBase(TestCase):
    def setUp(self):
        self.client = Client()

        self.organizador = User.objects.create_user(
            username="organizador",
            password="12345678",
            tipo="OR",
        )
        self.outro_organizador = User.objects.create_user(
            username="outro_organizador",
            password="12345678",
            tipo="OR",
        )
        self.gestor = User.objects.create_user(
            username="gestor",
            password="12345678",
            tipo="GE",
        )

        self.organizacao = Organizacao.objects.create(
            nome="Atlética Central",
            descricao="Organização de testes",
        )

        self.espaco = EspacoFisico.objects.create(
            nome="Quadra Central",
            localizacao="Campus Darcy Ribeiro",
            descricao="Quadra poliesportiva",
            status=EspacoFisico.Status.DISPONIVEL,
        )

        self.evento = Evento.objects.create(
            nome="Torneio de Vôlei",
            data=date.today() + timedelta(days=5),
            horario=time(14, 0),
            local="Quadra Central",
            organizador=self.organizador,
            organizacao=self.organizacao,
            capacidade=50,
        )

        self.inicio = timezone.now() + timedelta(days=1)
        self.fim = self.inicio + timedelta(hours=2)


class ReservasDoEventoTest(ReservasControllerTestBase):
    def test_reservas_do_evento_organizador_ok(self):
        self.client.force_login(self.organizador)

        response = self.client.get(
            reverse("reservas-do-evento", kwargs={"evento_id": self.evento.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/reservas/reservas_do_evento.html")
        self.assertEqual(response.context["evento"].id, self.evento.id)

    def test_reservas_do_evento_gestor_ok(self):
        self.client.force_login(self.gestor)

        response = self.client.get(
            reverse("reservas-do-evento", kwargs={"evento_id": self.evento.id})
        )

        self.assertEqual(response.status_code, 200)

    def test_reservas_do_evento_tipo_invalido_403(self):
        outro_tipo = User.objects.create_user(
            username="participante", password="12345678", tipo="PA"
        )
        self.client.force_login(outro_tipo)

        response = self.client.get(
            reverse("reservas-do-evento", kwargs={"evento_id": self.evento.id})
        )

        self.assertEqual(response.status_code, 403)

    def test_reservas_do_evento_nao_autenticado_redireciona_login(self):
        response = self.client.get(
            reverse("reservas-do-evento", kwargs={"evento_id": self.evento.id})
        )

        self.assertEqual(response.status_code, 302)

    def test_reservas_do_evento_404(self):
        self.client.force_login(self.gestor)

        response = self.client.get(
            reverse("reservas-do-evento", kwargs={"evento_id": uuid.uuid4()})
        )

        self.assertEqual(response.status_code, 404)


class SolicitarReservaTest(ReservasControllerTestBase):
    def test_solicitar_reserva_gestor_403(self):
        self.client.force_login(self.gestor)

        response = self.client.get(
            reverse("solicitar-reserva", kwargs={"evento_id": self.evento.id})
        )

        self.assertEqual(response.status_code, 403)

    def test_solicitar_reserva_get(self):
        self.client.force_login(self.organizador)

        response = self.client.get(
            reverse("solicitar-reserva", kwargs={"evento_id": self.evento.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/reservas/solicitar.html")

    def test_solicitar_reserva_post_valido(self):
        self.client.force_login(self.organizador)

        response = self.client.post(
            reverse("solicitar-reserva", kwargs={"evento_id": self.evento.id}),
            {
                "espaco": self.espaco.id,
                "data_inicio": self.inicio.strftime("%Y-%m-%dT%H:%M"),
                "data_fim": self.fim.strftime("%Y-%m-%dT%H:%M"),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(ReservaEspaco.objects.count(), 1)

        reserva = ReservaEspaco.objects.get()
        self.assertEqual(reserva.solicitante, self.organizador)
        self.assertEqual(reserva.status, ReservaEspaco.Status.PENDENTE)

    def test_solicitar_reserva_post_invalido(self):
        self.client.force_login(self.organizador)

        response = self.client.post(
            reverse("solicitar-reserva", kwargs={"evento_id": self.evento.id}),
            {},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/reservas/solicitar.html")
        self.assertTrue(response.context["form"].errors)

    def test_solicitar_reserva_post_conflito(self):
        ReservaEspaco.objects.create(
            espaco=self.espaco,
            evento=self.evento,
            solicitante=self.organizador,
            status=ReservaEspaco.Status.APROVADA,
            data_inicio=self.inicio,
            data_fim=self.fim,
        )

        self.client.force_login(self.organizador)

        response = self.client.post(
            reverse("solicitar-reserva", kwargs={"evento_id": self.evento.id}),
            {
                "espaco": self.espaco.id,
                "data_inicio": self.inicio.strftime("%Y-%m-%dT%H:%M"),
                "data_fim": self.fim.strftime("%Y-%m-%dT%H:%M"),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/reservas/solicitar.html")
        # Continua havendo apenas a reserva aprovada original.
        self.assertEqual(ReservaEspaco.objects.count(), 1)

    def test_solicitar_reserva_evento_404(self):
        self.client.force_login(self.organizador)

        response = self.client.get(
            reverse("solicitar-reserva", kwargs={"evento_id": uuid.uuid4()})
        )

        self.assertEqual(response.status_code, 404)


class MinhasReservasTest(ReservasControllerTestBase):
    def test_minhas_reservas_organizador_ok(self):
        ReservaEspaco.objects.create(
            espaco=self.espaco,
            evento=self.evento,
            solicitante=self.organizador,
            data_inicio=self.inicio,
            data_fim=self.fim,
        )

        self.client.force_login(self.organizador)

        response = self.client.get(reverse("minhas-reservas"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/reservas/minhas_reservas.html")
        self.assertEqual(len(response.context["reservas"]), 1)

    def test_minhas_reservas_gestor_403(self):
        self.client.force_login(self.gestor)

        response = self.client.get(reverse("minhas-reservas"))

        self.assertEqual(response.status_code, 403)


class CancelarReservaTest(ReservasControllerTestBase):
    def setUp(self):
        super().setUp()
        self.reserva = ReservaEspaco.objects.create(
            espaco=self.espaco,
            evento=self.evento,
            solicitante=self.organizador,
            data_inicio=self.inicio,
            data_fim=self.fim,
        )

    def test_cancelar_reserva_gestor_403(self):
        self.client.force_login(self.gestor)

        response = self.client.post(
            reverse("cancelar-reserva", kwargs={"reserva_id": self.reserva.id})
        )

        self.assertEqual(response.status_code, 403)

    def test_cancelar_reserva_pendente_ok(self):
        self.client.force_login(self.organizador)

        response = self.client.post(
            reverse("cancelar-reserva", kwargs={"reserva_id": self.reserva.id})
        )

        self.assertEqual(response.status_code, 302)
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.status, ReservaEspaco.Status.CANCELADA)

    def test_cancelar_reserva_nao_pendente_erro(self):
        self.reserva.status = ReservaEspaco.Status.APROVADA
        self.reserva.save(update_fields=["status"])

        self.client.force_login(self.organizador)

        response = self.client.post(
            reverse("cancelar-reserva", kwargs={"reserva_id": self.reserva.id})
        )

        self.assertEqual(response.status_code, 302)
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.status, ReservaEspaco.Status.APROVADA)

    def test_cancelar_reserva_de_outro_organizador_404(self):
        self.client.force_login(self.outro_organizador)

        response = self.client.post(
            reverse("cancelar-reserva", kwargs={"reserva_id": self.reserva.id})
        )

        self.assertEqual(response.status_code, 404)

    def test_cancelar_reserva_get_nao_permitido(self):
        self.client.force_login(self.organizador)

        response = self.client.get(
            reverse("cancelar-reserva", kwargs={"reserva_id": self.reserva.id})
        )

        self.assertEqual(response.status_code, 405)


class GestaoReservasListTest(ReservasControllerTestBase):
    def setUp(self):
        super().setUp()
        self.reserva_pendente = ReservaEspaco.objects.create(
            espaco=self.espaco,
            evento=self.evento,
            solicitante=self.organizador,
            status=ReservaEspaco.Status.PENDENTE,
            data_inicio=self.inicio,
            data_fim=self.fim,
        )
        self.reserva_aprovada = ReservaEspaco.objects.create(
            espaco=self.espaco,
            evento=self.evento,
            solicitante=self.organizador,
            status=ReservaEspaco.Status.APROVADA,
            avaliador=self.gestor,
            data_inicio=self.inicio + timedelta(days=10),
            data_fim=self.fim + timedelta(days=10),
        )

    def test_gestao_reservas_list_organizador_403(self):
        self.client.force_login(self.organizador)

        response = self.client.get(reverse("gestao-reservas-list"))

        self.assertEqual(response.status_code, 403)

    def test_gestao_reservas_list_sem_filtro(self):
        self.client.force_login(self.gestor)

        response = self.client.get(reverse("gestao-reservas-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["reservas"]), 2)
        self.assertEqual(response.context["status_filtro"], "")

    def test_gestao_reservas_list_com_filtro_valido(self):
        self.client.force_login(self.gestor)

        response = self.client.get(
            reverse("gestao-reservas-list"),
            {"status": ReservaEspaco.Status.APROVADA},
        )

        self.assertEqual(response.status_code, 200)
        reservas = list(response.context["reservas"])
        self.assertEqual(len(reservas), 1)
        self.assertEqual(reservas[0].id, self.reserva_aprovada.id)

    def test_gestao_reservas_list_com_filtro_invalido_ignora(self):
        self.client.force_login(self.gestor)

        response = self.client.get(
            reverse("gestao-reservas-list"),
            {"status": "status-invalido"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["reservas"]), 2)


class GestaoReservaDetalheTest(ReservasControllerTestBase):
    def setUp(self):
        super().setUp()
        self.reserva = ReservaEspaco.objects.create(
            espaco=self.espaco,
            evento=self.evento,
            solicitante=self.organizador,
            data_inicio=self.inicio,
            data_fim=self.fim,
        )

    def test_gestao_reserva_detalhe_organizador_403(self):
        self.client.force_login(self.organizador)

        response = self.client.get(
            reverse("gestao-reserva-detalhe", kwargs={"reserva_id": self.reserva.id})
        )

        self.assertEqual(response.status_code, 403)

    def test_gestao_reserva_detalhe_ok(self):
        self.client.force_login(self.gestor)

        response = self.client.get(
            reverse("gestao-reserva-detalhe", kwargs={"reserva_id": self.reserva.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/reservas/gestao_detalhe.html")
        self.assertIn("form_reprovacao", response.context)

    def test_gestao_reserva_detalhe_404(self):
        self.client.force_login(self.gestor)

        response = self.client.get(
            reverse("gestao-reserva-detalhe", kwargs={"reserva_id": uuid.uuid4()})
        )

        self.assertEqual(response.status_code, 404)


class AprovarReservaTest(ReservasControllerTestBase):
    def setUp(self):
        super().setUp()
        self.reserva = ReservaEspaco.objects.create(
            espaco=self.espaco,
            evento=self.evento,
            solicitante=self.organizador,
            status=ReservaEspaco.Status.PENDENTE,
            data_inicio=self.inicio,
            data_fim=self.fim,
        )

    def test_aprovar_reserva_organizador_403(self):
        self.client.force_login(self.organizador)

        response = self.client.post(
            reverse("aprovar-reserva", kwargs={"reserva_id": self.reserva.id})
        )

        self.assertEqual(response.status_code, 403)

    def test_aprovar_reserva_pendente_ok(self):
        self.client.force_login(self.gestor)

        response = self.client.post(
            reverse("aprovar-reserva", kwargs={"reserva_id": self.reserva.id})
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("gestao-reservas-list"))

        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.status, ReservaEspaco.Status.APROVADA)
        self.assertEqual(self.reserva.avaliador, self.gestor)

    def test_aprovar_reserva_com_next_relativo(self):
        self.client.force_login(self.gestor)
        destino = reverse(
            "gestao-reserva-detalhe", kwargs={"reserva_id": self.reserva.id}
        )

        response = self.client.post(
            reverse("aprovar-reserva", kwargs={"reserva_id": self.reserva.id}),
            {"next": destino},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, destino)

    def test_aprovar_reserva_nao_pendente_erro(self):
        self.reserva.status = ReservaEspaco.Status.REPROVADA
        self.reserva.save(update_fields=["status"])

        self.client.force_login(self.gestor)

        response = self.client.post(
            reverse("aprovar-reserva", kwargs={"reserva_id": self.reserva.id})
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("gestao-reservas-list"))

        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.status, ReservaEspaco.Status.REPROVADA)

    def test_aprovar_reserva_com_conflito(self):
        ReservaEspaco.objects.create(
            espaco=self.espaco,
            evento=self.evento,
            solicitante=self.outro_organizador,
            status=ReservaEspaco.Status.APROVADA,
            avaliador=self.gestor,
            data_inicio=self.inicio,
            data_fim=self.fim,
        )

        self.client.force_login(self.gestor)

        response = self.client.post(
            reverse("aprovar-reserva", kwargs={"reserva_id": self.reserva.id})
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("gestao-reserva-detalhe", kwargs={"reserva_id": self.reserva.id}),
        )

        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.status, ReservaEspaco.Status.PENDENTE)

    def test_aprovar_reserva_404(self):
        self.client.force_login(self.gestor)

        response = self.client.post(
            reverse("aprovar-reserva", kwargs={"reserva_id": uuid.uuid4()})
        )

        self.assertEqual(response.status_code, 404)


class ReprovarReservaTest(ReservasControllerTestBase):
    def setUp(self):
        super().setUp()
        self.reserva = ReservaEspaco.objects.create(
            espaco=self.espaco,
            evento=self.evento,
            solicitante=self.organizador,
            status=ReservaEspaco.Status.PENDENTE,
            data_inicio=self.inicio,
            data_fim=self.fim,
        )

    def test_reprovar_reserva_organizador_403(self):
        self.client.force_login(self.organizador)

        response = self.client.post(
            reverse("reprovar-reserva", kwargs={"reserva_id": self.reserva.id})
        )

        self.assertEqual(response.status_code, 403)

    def test_reprovar_reserva_nao_pendente_erro(self):
        self.reserva.status = ReservaEspaco.Status.APROVADA
        self.reserva.save(update_fields=["status"])

        self.client.force_login(self.gestor)

        response = self.client.post(
            reverse("reprovar-reserva", kwargs={"reserva_id": self.reserva.id}),
            {"motivo_reprovacao": "Conflito de agenda"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("gestao-reservas-list"))

        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.status, ReservaEspaco.Status.APROVADA)

    def test_reprovar_reserva_valido_sem_next(self):
        self.client.force_login(self.gestor)

        response = self.client.post(
            reverse("reprovar-reserva", kwargs={"reserva_id": self.reserva.id}),
            {"motivo_reprovacao": "Espaço indisponível para manutenção"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("gestao-reservas-list"))

        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.status, ReservaEspaco.Status.REPROVADA)
        self.assertEqual(self.reserva.avaliador, self.gestor)
        self.assertEqual(
            self.reserva.motivo_reprovacao, "Espaço indisponível para manutenção"
        )

    def test_reprovar_reserva_valido_com_next_relativo(self):
        self.client.force_login(self.gestor)
        destino = reverse("minhas-reservas")

        response = self.client.post(
            reverse("reprovar-reserva", kwargs={"reserva_id": self.reserva.id}),
            {"motivo_reprovacao": "Motivo válido", "next": destino},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, destino)

    def test_reprovar_reserva_invalido_sem_next(self):
        # motivo_reprovacao é blank=True no model, então o form nunca fica
        # inválido "naturalmente" só por vir vazio; forçamos is_valid=False
        # para exercitar o ramo de erro do controller.
        self.client.force_login(self.gestor)

        with patch(
            "apps.core.controllers.reservas_controller.ReprovacaoReservaForm.is_valid",
            return_value=False,
        ):
            response = self.client.post(
                reverse("reprovar-reserva", kwargs={"reserva_id": self.reserva.id}),
                {"motivo_reprovacao": ""},
            )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("gestao-reserva-detalhe", kwargs={"reserva_id": self.reserva.id}),
        )

        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.status, ReservaEspaco.Status.PENDENTE)

    def test_reprovar_reserva_invalido_com_next_relativo(self):
        self.client.force_login(self.gestor)
        destino = reverse("minhas-reservas")

        with patch(
            "apps.core.controllers.reservas_controller.ReprovacaoReservaForm.is_valid",
            return_value=False,
        ):
            response = self.client.post(
                reverse("reprovar-reserva", kwargs={"reserva_id": self.reserva.id}),
                {"motivo_reprovacao": "", "next": destino},
            )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, destino)

        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.status, ReservaEspaco.Status.PENDENTE)

    def test_reprovar_reserva_404(self):
        self.client.force_login(self.gestor)

        response = self.client.post(
            reverse("reprovar-reserva", kwargs={"reserva_id": uuid.uuid4()}),
            {"motivo_reprovacao": "Motivo qualquer"},
        )

        self.assertEqual(response.status_code, 404)
