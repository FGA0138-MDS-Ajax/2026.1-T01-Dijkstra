from datetime import date, time, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.core.forms import EventoForm, ReservaEspacoForm
from apps.core.models.eventos_models import Evento
from apps.core.models.organizacoes_models import Organizacao

User = get_user_model()


class EventoFormOrganizadorTest(TestCase):
    def setUp(self):
        self.organizador = User.objects.create_user(
            username="organizador_form",
            password="12345678",
            tipo="OR",
        )
        self.organizacao = Organizacao.objects.create(
            nome="Organização Form", descricao="Teste"
        )
        self.organizacao.membros.create(usuario=self.organizador)

        self.evento = Evento.objects.create(
            nome="Evento Existente",
            data=date.today(),
            horario=time(10, 0),
            local="Auditório",
            organizador=self.organizador,
            organizacao=self.organizacao,
            capacidade=10,
        )

    def test_sem_usuario_e_sem_instancia_queryset_vazio(self):
        """Cobre o ramo 'else: queryset = Organizacao.objects.none()'."""
        form = EventoForm()

        self.assertEqual(form.fields["organizacao"].queryset.count(), 0)

    def test_instancia_com_organizador_usa_organizador_da_instancia(self):
        """Cobre 'organizador = self.instance.organizador' quando usuario=None."""
        form = EventoForm(instance=self.evento)

        self.assertIn(self.organizacao, form.fields["organizacao"].queryset)

    def test_usuario_explicito_tem_prioridade(self):
        form = EventoForm(usuario=self.organizador)

        self.assertIn(self.organizacao, form.fields["organizacao"].queryset)


class ReservaEspacoFormCleanTest(TestCase):
    def setUp(self):
        from apps.core.models.espacos_models import EspacoFisico

        self.espaco = EspacoFisico.objects.create(
            nome="Quadra Form",
            localizacao="Bloco A",
            descricao="Teste",
            status=EspacoFisico.Status.DISPONIVEL,
        )

    def test_clean_data_fim_anterior_a_inicio_invalido(self):
        inicio = timezone.now() + timedelta(days=1)
        fim = inicio - timedelta(hours=1)

        form = ReservaEspacoForm(
            data={
                "espaco": self.espaco.id,
                "data_inicio": inicio.strftime("%Y-%m-%dT%H:%M"),
                "data_fim": fim.strftime("%Y-%m-%dT%H:%M"),
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            "A data/hora de término deve ser posterior à de início.",
            form.non_field_errors(),
        )

    def test_clean_data_fim_igual_inicio_invalido(self):
        momento = timezone.now() + timedelta(days=1)

        form = ReservaEspacoForm(
            data={
                "espaco": self.espaco.id,
                "data_inicio": momento.strftime("%Y-%m-%dT%H:%M"),
                "data_fim": momento.strftime("%Y-%m-%dT%H:%M"),
            }
        )

        self.assertFalse(form.is_valid())

    def test_clean_datas_validas(self):
        inicio = timezone.now() + timedelta(days=1)
        fim = inicio + timedelta(hours=2)

        form = ReservaEspacoForm(
            data={
                "espaco": self.espaco.id,
                "data_inicio": inicio.strftime("%Y-%m-%dT%H:%M"),
                "data_fim": fim.strftime("%Y-%m-%dT%H:%M"),
            }
        )

        self.assertTrue(form.is_valid())
