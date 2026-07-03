from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class CadastroControllerTest(TestCase):
    def setUp(self):
        # Evita que o rate limit (5/min por IP) de um teste vaze para outro.
        cache.clear()
        self.client = Client()

    def test_cadastro_get_nao_autenticado(self):
        response = self.client.get(reverse("cadastro"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "security/cadastro.html")
        self.assertIn("form", response.context)

    def test_cadastro_get_autenticado_redireciona(self):
        usuario = User.objects.create_user(
            username="190012345",
            matricula="190012345",
            nome_completo="Usuário Teste",
            password="12345678",
        )
        self.client.force_login(usuario)

        response = self.client.get(reverse("cadastro"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("area-restrita-perfil"))

    def test_cadastro_post_valido_cria_usuario_e_redireciona_login(self):
        response = self.client.post(
            reverse("cadastro"),
            {
                "matricula": "190012345",
                "password": "senha1234",
                "confirmar_senha": "senha1234",
                "termos_uso": True,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("login"))
        self.assertTrue(User.objects.filter(matricula="190012345").exists())

    def test_cadastro_post_invalido_renderiza_erros(self):
        response = self.client.post(
            reverse("cadastro"),
            {
                "matricula": "abc",
                "password": "senha1234",
                "confirmar_senha": "outrasenha",
                "termos_uso": True,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "security/cadastro.html")
        self.assertTrue(response.context["form"].errors)
        self.assertFalse(User.objects.filter(matricula="abc").exists())
