from django.test import TestCase

from apps.security.forms import CadastroForm
from apps.security.models.usuario_models import TipoPerfil, Usuario


class CadastroFormTest(TestCase):
    def _dados_validos(self, **overrides):
        dados = {
            "matricula": "190012345",
            "password": "senha1234",
            "confirmar_senha": "senha1234",
            "termos_uso": True,
        }
        dados.update(overrides)
        return dados

    def test_form_valido(self):
        form = CadastroForm(data=self._dados_validos())

        self.assertTrue(form.is_valid())

    def test_clean_matricula_ja_cadastrada(self):
        Usuario.objects.create_user(
            username="190012345",
            matricula="190012345",
            nome_completo="Usuário Existente",
            password="12345678",
        )

        form = CadastroForm(data=self._dados_validos())

        self.assertFalse(form.is_valid())
        self.assertIn("matricula", form.errors)
        self.assertIn(
            "Esta matrícula já está cadastrada no sistema.",
            form.errors["matricula"],
        )

    def test_clean_senhas_nao_coincidem(self):
        form = CadastroForm(data=self._dados_validos(confirmar_senha="outrasenha123"))

        self.assertFalse(form.is_valid())
        self.assertIn("confirmar_senha", form.errors)
        self.assertIn(
            "As senhas não coincidem.",
            form.errors["confirmar_senha"],
        )

    def test_clean_sem_senha_nao_valida_coincidencia(self):
        """Quando a senha em si já é inválida, o clean() não deve quebrar."""
        form = CadastroForm(data=self._dados_validos(password="", confirmar_senha=""))

        self.assertFalse(form.is_valid())
        self.assertNotIn(
            "As senhas não coincidem.",
            form.errors.get("confirmar_senha", []),
        )

    def test_save_cria_usuario(self):
        form = CadastroForm(data=self._dados_validos())
        self.assertTrue(form.is_valid())

        usuario = form.save()

        self.assertEqual(usuario.username, "190012345")
        self.assertEqual(usuario.matricula, "190012345")
        self.assertEqual(usuario.nome_completo, "Usuário 190012345")
        self.assertEqual(usuario.tipo, TipoPerfil.ALUNO)
        self.assertTrue(usuario.is_active)
        self.assertTrue(usuario.check_password("senha1234"))
