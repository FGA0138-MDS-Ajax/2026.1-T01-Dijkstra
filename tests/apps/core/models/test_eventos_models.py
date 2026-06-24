from datetime import date, time

from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.core.models.eventos_models import Evento
from apps.core.models.organizacoes_models import Organizacao


class TestEventoModel(TestCase):
    def setUp(self):
        self.organizador = get_user_model().objects.create_user(
            username="org_user",
            password="senha123",
            tipo="OR",
            nome_completo="Liga Universitária de Esportes",
        )
        self.organizacao = Organizacao.objects.create(
            nome="Liga Universitária de Esportes",
            descricao="Organização de teste.",
        )
        self.evento = Evento.objects.create(
            nome="Torneio Universitário de Futsal",
            data=date(2026, 8, 15),
            horario=time(9, 0),
            local="Ginásio Darcy Ribeiro",
            organizador=self.organizador,
            organizacao=self.organizacao,
            descricao="Torneio interuniversitário de futsal masculino e feminino.",
            capacidade=200,
        )

    def test_str(self):
        self.assertEqual(
            str(self.evento),
            "Torneio Universitário de Futsal",
        )

    def test_status_default(self):
        self.assertEqual(
            self.evento.status,
            Evento.Status.RASCUNHO,
        )

    def test_campos_automaticos(self):
        self.assertIsNotNone(self.evento.id)
        self.assertIsNotNone(self.evento.criado_em)
        self.assertIsNotNone(self.evento.atualizado_em)

    def test_verbose_name(self):
        self.assertEqual(
            Evento._meta.verbose_name,
            "Evento",
        )

    def test_verbose_name_plural(self):
        self.assertEqual(
            Evento._meta.verbose_name_plural,
            "Eventos",
        )

    def test_ordering(self):
        self.assertEqual(
            Evento._meta.ordering,
            ["-data", "-horario"],
        )
