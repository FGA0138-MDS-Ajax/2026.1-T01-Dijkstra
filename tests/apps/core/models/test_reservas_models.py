from datetime import date, time, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.core.models.espacos_models import EspacoFisico
from apps.core.models.eventos_models import Evento
from apps.core.models.organizacoes_models import Organizacao
from apps.core.models.reservas_models import ReservaEspaco

User = get_user_model()


class ReservaEspacoModelTest(TestCase):
    def test_str(self):
        organizador = User.objects.create_user(
            username="organizador_model",
            password="12345678",
            tipo="OR",
        )
        organizacao = Organizacao.objects.create(
            nome="Organização Model", descricao="Teste"
        )
        espaco = EspacoFisico.objects.create(
            nome="Quadra Model",
            localizacao="Bloco A",
            descricao="Teste",
            status=EspacoFisico.Status.DISPONIVEL,
        )
        evento = Evento.objects.create(
            nome="Evento Model",
            data=date.today(),
            horario=time(10, 0),
            local="Auditório",
            organizador=organizador,
            organizacao=organizacao,
            capacidade=10,
        )
        inicio = timezone.now() + timedelta(days=1)
        fim = inicio + timedelta(hours=2)

        reserva = ReservaEspaco.objects.create(
            espaco=espaco,
            evento=evento,
            solicitante=organizador,
            data_inicio=inicio,
            data_fim=fim,
        )

        texto = str(reserva)

        self.assertIn(espaco.nome, texto)
        self.assertIn(evento.nome, texto)
        self.assertIn(inicio.strftime("%d/%m/%Y %H:%M"), texto)
        self.assertIn(fim.strftime("%H:%M"), texto)
