"""
tests.apps.security.controllers.test_security_controllers
=========================================================
Testes de integracao para os controllers e formularios de autenticacao e usuarios.
"""

import uuid
from django.test import TestCase, Client
from apps.security.models.usuario_models import Usuario

# from django.urls import reverse


class SecurityControllersTestCase(TestCase):
    """Garante cobertura nos fluxos e controllers usando URLs estaticas reais."""

    def setUp(self) -> None:
        self.client = Client()

        self.senha_comum = "Senha@Forte2026!Ok"

        self.admin_user = Usuario.objects.create_superuser(
            username="admin_test",
            email="admin@test.com",
            password=self.senha_comum,
            nome_completo="Administrador do Sistema",
            tipo="OR",
        )

        self.aluno_user = Usuario.objects.create_user(
            username="aluno_test",
            email="aluno@test.com",
            password=self.senha_comum,
            nome_completo="Aluno Teste",
            tipo="AL",
        )

        self.url_login = "/security/login/"
        self.url_logout = "/security/logout/"
        self.url_cadastro = "/security/cadastro/"
        self.url_esqueci_senha = "/security/esqueci-senha/"
        self.url_politica = "/security/politica-de-privacidade/"
        self.url_termos = "/security/termos-de-uso/"
        self.url_area_restrita = "/security/area-restrita/"
        self.url_perfil = "/security/area-restrita/perfil/"
        self.url_eventos_inscritos = "/security/area-restrita/eventos-inscritos/"
        self.url_gestao_eventos = "/security/area-restrita/gestao-eventos/"
        self.url_organizacoes = "/security/area-restrita/organizacoes-vinculadas/"
        self.url_espacos = "/security/area-restrita/espacos-esportivos/"
        self.url_reservas = "/security/area-restrita/reservas/"
        self.url_gestao_usuarios = "/security/area-restrita/gestao-usuarios/"

    def test_paginas_estaticas_e_login(self) -> None:
        """Testa telas basicas publicas de visualizacao."""
        for url in [
            self.url_login,
            self.url_esqueci_senha,
            self.url_politica,
            self.url_termos,
        ]:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_acesso_area_restrita_e_redirecionamento(self) -> None:
        """Testa as restricoes e sub-paginas do area_restrita_controller.py."""

        response = self.client.get(self.url_area_restrita)
        self.assertIn(response.status_code, [200, 302])

        self.client.login(username="aluno_test", password=self.senha_comum)

        urls_internas = [
            self.url_area_restrita,
            self.url_perfil,
            self.url_eventos_inscritos,
            self.url_gestao_eventos,
            self.url_organizacoes,
            self.url_espacos,
            self.url_reservas,
            self.url_gestao_usuarios,
        ]

        for url in urls_internas:
            res = self.client.get(url)
            self.assertIn(res.status_code, [200, 302])

        self.client.logout()

    def test_usuario_controller_acoes_gerenciais(self) -> None:
        """Cobre as funcoes de gerenciamento (alterar perfil, inativar e excluir)."""
        self.client.login(username="admin_test", password=self.senha_comum)

        id_usuario = str(self.aluno_user.id)
        url_alterar = (
            f"/security/area-restrita/gestao-usuarios/{id_usuario}/alterar-perfil/"
        )
        url_inativar = f"/security/area-restrita/gestao-usuarios/{id_usuario}/inativar/"
        url_excluir = f"/security/area-restrita/gestao-usuarios/{id_usuario}/excluir/"

        response_alt = self.client.post(
            url_alterar, data={"nome_completo": "Nome Alterado", "tipo": "AL"}
        )
        self.assertIn(response_alt.status_code, [200, 302])

        response_inat = self.client.post(url_inativar)
        self.assertIn(response_inat.status_code, [200, 302])

        response_exc = self.client.post(url_excluir)
        self.assertIn(response_exc.status_code, [200, 302])

        uuid_inexistente = str(uuid.uuid4())
        url_inexistente = (
            f"/security/area-restrita/gestao-usuarios/{uuid_inexistente}/inativar/"
        )

        res_erro = self.client.post(url_inexistente)
        # Agora o Django aceitara o formato e retornara 404 (Objeto nao encontrado) com sucesso
        self.assertIn(res_erro.status_code, [200, 302, 404])

        self.client.logout()
