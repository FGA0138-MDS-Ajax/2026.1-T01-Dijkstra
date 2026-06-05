# tests/apps/core/models/test_organizacoes_models.py

from django.test import TestCase

from apps.core.models.organizacoes_models import Organizacao


class OrganizacaoModelTest(TestCase):
    def setUp(self):
        self.organizacao = Organizacao.objects.create(
            nome="Titans do Patins",
            descricao="Organização esportiva universitária",
        )

    def test_criacao_organizacao(self):
        self.assertIsNotNone(self.organizacao.id)

    def test_nome(self):
        self.assertEqual(
            self.organizacao.nome,
            "Titans do Patins",
        )

    def test_descricao(self):
        self.assertEqual(
            self.organizacao.descricao,
            "Organização esportiva universitária",
        )

    def test_foto_padrao(self):
        self.assertFalse(self.organizacao.foto)

    def test_str(self):
        self.assertEqual(
            str(self.organizacao),
            "Titans do Patins",
        )

    def test_verbose_name(self):
        self.assertEqual(
            Organizacao._meta.verbose_name,
            "Organização",
        )

    def test_verbose_name_plural(self):
        self.assertEqual(
            Organizacao._meta.verbose_name_plural,
            "Organizações",
        )

    def test_ordering(self):
        self.assertEqual(
            Organizacao._meta.ordering,
            ["nome"],
        )
