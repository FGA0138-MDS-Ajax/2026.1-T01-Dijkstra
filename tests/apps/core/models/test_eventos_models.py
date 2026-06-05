from datetime import date, time

from django.test import TestCase

from apps.core.models.eventos_models import Evento


class TestEventoModel(TestCase):
    def setUp(self):
        self.evento = Evento.objects.create(
            nome="Torneio Universitário de Futsal",
            data=date(2026, 8, 15),
            horario=time(9, 0),
            local="Ginásio Darcy Ribeiro",
            organizador="Liga Universitária de Esportes",
            gestor="Coordenação de Esportes UnB",
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
