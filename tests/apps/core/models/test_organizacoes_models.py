# tests/apps/core/models/test_organizacoes_models.py

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from apps.core.models.organizacoes_models import Organizacao, UsuarioOrganizacao

Usuario = get_user_model()


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


class UsuarioOrganizacaoModelTest(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="org_user",
            password="senha123",
            tipo="OR",
        )
        self.organizacao = Organizacao.objects.create(
            nome="Atlética FGA",
            descricao="Organização esportiva",
        )
        self.vinculo = UsuarioOrganizacao.objects.create(
            usuario=self.usuario,
            organizacao=self.organizacao,
        )

    def test_criacao_vinculo(self):
        self.assertIsNotNone(self.vinculo.pk)

    def test_str(self):
        esperado = f"{self.usuario} -> {self.organizacao}"
        self.assertEqual(str(self.vinculo), esperado)

    def test_verbose_name(self):
        self.assertEqual(
            UsuarioOrganizacao._meta.verbose_name,
            "Membro de Organizacao",
        )

    def test_verbose_name_plural(self):
        self.assertEqual(
            UsuarioOrganizacao._meta.verbose_name_plural,
            "Membros de Organizacoes",
        )

    def test_unique_together_impede_duplicata(self):
        with self.assertRaises(IntegrityError):
            UsuarioOrganizacao.objects.create(
                usuario=self.usuario,
                organizacao=self.organizacao,
            )

    def test_cascade_deleta_vinculo_ao_remover_usuario(self):
        self.usuario.delete()
        self.assertFalse(
            UsuarioOrganizacao.objects.filter(pk=self.vinculo.pk).exists()
        )

    def test_cascade_deleta_vinculo_ao_remover_organizacao(self):
        self.organizacao.delete()
        self.assertFalse(
            UsuarioOrganizacao.objects.filter(pk=self.vinculo.pk).exists()
        )

    def test_related_name_membros(self):
        self.assertIn(self.vinculo, self.organizacao.membros.all())

    def test_related_name_organizacoes_vinculadas(self):
        self.assertIn(self.vinculo, self.usuario.organizacoes_vinculadas.all())
