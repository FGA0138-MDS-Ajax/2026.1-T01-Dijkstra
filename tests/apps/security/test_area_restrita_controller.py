import uuid

from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from apps.security.controllers.area_restrita_controller import (
    politica_privacidade,
    termos_de_uso,
)

User = get_user_model()


class AreaRestritaAcessoPorPerfilTest(TestCase):
    """Cobre os ramos de acesso concedido (não apenas o redirect de negação)."""

    def setUp(self):
        self.client = Client()
        self.senha = "Senha@Forte2026!Ok"

        self.organizador = User.objects.create_user(
            username="organizador_area",
            password=self.senha,
            nome_completo="Organizador Teste",
            tipo="OR",
        )
        self.gestor = User.objects.create_user(
            username="gestor_area",
            password=self.senha,
            nome_completo="Gestor Teste",
            tipo="GE",
        )

    def test_eventos_inscritos_nao_aluno_redireciona(self):
        self.client.login(username="organizador_area", password=self.senha)

        response = self.client.get(reverse("area-restrita-eventos-inscritos"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("area-restrita-perfil"))

    def test_gestao_eventos_organizador_acessa(self):
        self.client.login(username="organizador_area", password=self.senha)

        response = self.client.get(reverse("area-restrita-gestao-eventos"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "security/area_restrita/gestao_eventos.html")
        self.assertIn("eventos", response.context)

    def test_organizacoes_vinculadas_organizador_acessa(self):
        self.client.login(username="organizador_area", password=self.senha)

        response = self.client.get(reverse("area-restrita-organizacoes-vinculadas"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "security/area_restrita/organizacoes_vinculadas.html"
        )
        self.assertIn("organizacoes", response.context)

    def test_espacos_esportivos_gestor_acessa(self):
        self.client.login(username="gestor_area", password=self.senha)

        response = self.client.get(reverse("area-restrita-espacos-esportivos"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "security/area_restrita/espacos_esportivos.html"
        )
        self.assertIn("espacos", response.context)

    def test_reservas_gestor_sem_filtro(self):
        self.client.login(username="gestor_area", password=self.senha)

        response = self.client.get(reverse("area-restrita-reservas"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "security/area_restrita/reservas.html")
        self.assertEqual(response.context["status_filtro"], "")
        self.assertEqual(response.context["espaco_filtro"], "")

    def test_reservas_gestor_com_filtro_status_valido(self):
        from apps.core.models.reservas_models import ReservaEspaco

        self.client.login(username="gestor_area", password=self.senha)

        response = self.client.get(
            reverse("area-restrita-reservas"),
            {"status": ReservaEspaco.Status.PENDENTE},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["status_filtro"], ReservaEspaco.Status.PENDENTE
        )

    def test_reservas_gestor_com_filtro_espaco(self):
        self.client.login(username="gestor_area", password=self.senha)
        espaco_id = uuid.uuid4()

        response = self.client.get(
            reverse("area-restrita-reservas"),
            {"espaco": str(espaco_id)},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["espaco_filtro"], str(espaco_id))

    def test_gestao_usuarios_gestor_acessa(self):
        self.client.login(username="gestor_area", password=self.senha)

        response = self.client.get(reverse("area-restrita-gestao-usuarios"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "security/area_restrita/gestao_usuarios.html")
        self.assertIn("usuarios", response.context)
        self.assertIn("perfis", response.context)


class GestaoUsuariosAcoesTest(TestCase):
    """Cobre os ramos de negação de acesso e auto/superuser-proteção das ações."""

    def setUp(self):
        self.client = Client()
        self.senha = "Senha@Forte2026!Ok"

        self.gestor = User.objects.create_user(
            username="gestor_acoes",
            password=self.senha,
            nome_completo="Gestor Ações",
            tipo="GE",
        )
        self.aluno = User.objects.create_user(
            username="aluno_acoes",
            password=self.senha,
            nome_completo="Aluno Ações",
            tipo="AL",
        )
        self.superuser_alvo = User.objects.create_superuser(
            username="super_alvo",
            email="super@teste.com",
            password=self.senha,
            nome_completo="Super Alvo",
            tipo="GE",
        )

    # -- alterar_perfil_usuario -------------------------------------------------

    def test_alterar_perfil_nao_gestor_redireciona(self):
        self.client.login(username="aluno_acoes", password=self.senha)

        response = self.client.post(
            reverse(
                "area-restrita-alterar-perfil-usuario",
                kwargs={"usuario_id": str(self.aluno.pk)},
            ),
            {"tipo": "OR"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("area-restrita-perfil"))

    def test_alterar_perfil_alvo_superuser_bloqueado(self):
        self.client.login(username="gestor_acoes", password=self.senha)

        response = self.client.post(
            reverse(
                "area-restrita-alterar-perfil-usuario",
                kwargs={"usuario_id": str(self.superuser_alvo.pk)},
            ),
            {"tipo": "OR"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("area-restrita-gestao-usuarios"))
        self.superuser_alvo.refresh_from_db()
        self.assertEqual(self.superuser_alvo.tipo, "GE")

    def test_alterar_perfil_tipo_invalido(self):
        self.client.login(username="gestor_acoes", password=self.senha)

        response = self.client.post(
            reverse(
                "area-restrita-alterar-perfil-usuario",
                kwargs={"usuario_id": str(self.aluno.pk)},
            ),
            {"tipo": "TIPO_INEXISTENTE"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("area-restrita-gestao-usuarios"))
        self.aluno.refresh_from_db()
        self.assertEqual(self.aluno.tipo, "AL")

    def test_alterar_perfil_valido(self):
        self.client.login(username="gestor_acoes", password=self.senha)

        response = self.client.post(
            reverse(
                "area-restrita-alterar-perfil-usuario",
                kwargs={"usuario_id": str(self.aluno.pk)},
            ),
            {"tipo": "OR"},
        )

        self.assertEqual(response.status_code, 302)
        self.aluno.refresh_from_db()
        self.assertEqual(self.aluno.tipo, "OR")

    # -- inativar_usuario ---------------------------------------------------

    def test_inativar_nao_gestor_redireciona(self):
        self.client.login(username="aluno_acoes", password=self.senha)

        response = self.client.post(
            reverse(
                "area-restrita-inativar-usuario",
                kwargs={"usuario_id": str(self.aluno.pk)},
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("area-restrita-perfil"))

    def test_inativar_alvo_superuser_bloqueado(self):
        self.client.login(username="gestor_acoes", password=self.senha)

        response = self.client.post(
            reverse(
                "area-restrita-inativar-usuario",
                kwargs={"usuario_id": str(self.superuser_alvo.pk)},
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("area-restrita-gestao-usuarios"))
        self.superuser_alvo.refresh_from_db()
        self.assertTrue(self.superuser_alvo.is_active)

    def test_inativar_valido_alterna_status(self):
        self.client.login(username="gestor_acoes", password=self.senha)

        response = self.client.post(
            reverse(
                "area-restrita-inativar-usuario",
                kwargs={"usuario_id": str(self.aluno.pk)},
            )
        )

        self.assertEqual(response.status_code, 302)
        self.aluno.refresh_from_db()
        self.assertFalse(self.aluno.is_active)

    # -- excluir_usuario ------------------------------------------------------

    def test_excluir_nao_gestor_redireciona(self):
        self.client.login(username="aluno_acoes", password=self.senha)

        response = self.client.post(
            reverse(
                "area-restrita-excluir-usuario",
                kwargs={"usuario_id": str(self.aluno.pk)},
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("area-restrita-perfil"))
        self.assertTrue(User.objects.filter(pk=self.aluno.pk).exists())

    def test_excluir_alvo_superuser_bloqueado(self):
        self.client.login(username="gestor_acoes", password=self.senha)

        response = self.client.post(
            reverse(
                "area-restrita-excluir-usuario",
                kwargs={"usuario_id": str(self.superuser_alvo.pk)},
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("area-restrita-gestao-usuarios"))
        self.assertTrue(User.objects.filter(pk=self.superuser_alvo.pk).exists())

    def test_excluir_valido_remove_usuario(self):
        self.client.login(username="gestor_acoes", password=self.senha)

        response = self.client.post(
            reverse(
                "area-restrita-excluir-usuario",
                kwargs={"usuario_id": str(self.aluno.pk)},
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(pk=self.aluno.pk).exists())


class PaginasEstaticasNaoRoteadasTest(TestCase):
    """
    termos_de_uso e politica_privacidade não estão ligadas no urls.py
    (que usa TemplateView diretamente), mas seguem no controller.
    Chamamos as funções diretamente para cobrir esse código.
    """

    def setUp(self):
        self.factory = RequestFactory()

    def test_termos_de_uso(self):
        request = self.factory.get("/qualquer-caminho/")

        response = termos_de_uso(request)

        self.assertEqual(response.status_code, 200)

    def test_politica_privacidade(self):
        request = self.factory.get("/qualquer-caminho/")

        response = politica_privacidade(request)

        self.assertEqual(response.status_code, 200)
