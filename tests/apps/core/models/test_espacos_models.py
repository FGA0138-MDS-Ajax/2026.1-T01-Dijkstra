from django.test import TestCase

from apps.core.models.espacos_models import EspacoFisico


class TestEspacoFisicoModel(TestCase):
    def setUp(self):
        self.espaco = EspacoFisico.objects.create(
            nome="Quadra Poli-esportiva",
            localizacao="FCTE",
            descricao="Quadra poli-esportiva",
        )

    def test_str(self):
        self.assertEqual(
            str(self.espaco),
            "Quadra Poli-esportiva",
        )

    def test_status_default(self):
        self.assertEqual(
            self.espaco.status,
            EspacoFisico.Status.DISPONIVEL,
        )

    def test_status_display_disponivel(self):
        self.espaco.status = EspacoFisico.Status.DISPONIVEL

        self.assertEqual(
            self.espaco.status_display,
            "Disponível",
        )

    def test_status_display_em_manutencao(self):
        self.espaco.status = EspacoFisico.Status.EM_MANUTENCAO

        self.assertEqual(
            self.espaco.status_display,
            "Em Manutenção",
        )

    def test_status_display_desativado(self):
        self.espaco.status = EspacoFisico.Status.DESATIVADO

        self.assertEqual(
            self.espaco.status_display,
            "Desativado",
        )

    def test_status_css_class_disponivel(self):
        self.espaco.status = EspacoFisico.Status.DISPONIVEL

        self.assertEqual(
            self.espaco.status_css_class,
            "status-disponivel",
        )

    def test_status_css_class_em_manutencao(self):
        self.espaco.status = EspacoFisico.Status.EM_MANUTENCAO

        self.assertEqual(
            self.espaco.status_css_class,
            "status-manutencao",
        )

    def test_status_css_class_desativado(self):
        self.espaco.status = EspacoFisico.Status.DESATIVADO

        self.assertEqual(
            self.espaco.status_css_class,
            "status-desativado",
        )

    def test_status_css_class_desconhecido(self):
        self.espaco.status = "status_invalido"

        self.assertEqual(
            self.espaco.status_css_class,
            "",
        )

    def test_campos_automaticos(self):
        self.assertIsNotNone(
            self.espaco.id,
        )

        self.assertIsNotNone(
            self.espaco.criado_em,
        )

        self.assertIsNotNone(
            self.espaco.atualizado_em,
        )

