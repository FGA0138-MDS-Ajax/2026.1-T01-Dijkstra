from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.core.models.eventos_models import Evento
from apps.core.models.inscricao_models import Inscricao
from apps.core.models.organizacoes_models import Organizacao

User = get_user_model()


class InscricaoModelTest(TestCase):
    def test_str(self):
        organizador = User.objects.create_user(
            username="organizador_inscricao_model",
            password="12345678",
            tipo="OR",
        )
        aluno = User.objects.create_user(
            username="aluno_inscricao_model",
            password="12345678",
            tipo="AL",
        )
        organizacao = Organizacao.objects.create(
            nome="Organização Inscrição Model", descricao="Teste"
        )
        evento = Evento.objects.create(
            nome="Evento Inscrição Model",
            data=date.today(),
            horario=time(10, 0),
            local="Auditório",
            organizador=organizador,
            organizacao=organizacao,
            capacidade=10,
        )

        inscricao = Inscricao.objects.create(
            aluno=aluno,
            evento=evento,
            status=Inscricao.Status.PENDENTE,
        )

        texto = str(inscricao)

        self.assertIn(str(aluno), texto)
        self.assertIn(evento.nome, texto)
        self.assertIn(inscricao.get_status_display(), texto)
