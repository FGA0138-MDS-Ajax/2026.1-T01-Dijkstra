"""
tests.apps.security.controllers.test_usuario_controller
=========================================================
Testes de unidade para UsuarioController e UsuarioDetalheController.

Essas views nao estao registradas em nenhum ``urls.py`` do projeto (nao
sao roteadas via HTTP em producao), entao os testes as instanciam
diretamente com ``RequestFactory`` para garantir cobertura de todos os
ramos de codigo.
"""

import json
import uuid

from django.test import TestCase, RequestFactory

from apps.security.controllers.usuario_controller import (
    UsuarioController,
    UsuarioDetalheController,
)
from apps.security.models.usuario_models import Usuario


class UsuarioControllerTestCase(TestCase):
    """Testes para a view de listagem/criacao (UsuarioController)."""

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.view = UsuarioController.as_view()

    def test_get_lista_usuarios_vazia(self) -> None:
        """Sem usuarios adicionais, retorna apenas os ja existentes via migration (se houver)."""
        request = self.factory.get("/api/usuarios/")
        response = self.view(request)
        dados = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(dados), Usuario.objects.count())

    def test_get_lista_usuarios_com_dados(self) -> None:
        """Com um usuario novo cadastrado, ele aparece corretamente serializado na lista."""
        total_antes = Usuario.objects.count()
        usuario = Usuario.objects.create_user(
            username="usuario_lista",
            email="lista@test.com",
            password="SenhaForte123!",
            nome_completo="Usuario Lista",
            tipo="AL",
        )

        request = self.factory.get("/api/usuarios/")
        response = self.view(request)
        dados = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(dados), total_antes + 1)

        dados_usuario = next(d for d in dados if d["id"] == str(usuario.id))
        self.assertEqual(dados_usuario["username"], "usuario_lista")
        self.assertEqual(dados_usuario["nome_completo"], "Usuario Lista")
        self.assertEqual(dados_usuario["tipo"], "AL")
        self.assertTrue(dados_usuario["is_active"])
        self.assertTrue(dados_usuario["is_aluno"])
        self.assertFalse(dados_usuario["is_organizador"])
        self.assertFalse(dados_usuario["is_gestor"])

    def test_post_cria_usuario_com_sucesso(self) -> None:
        """Cria um usuario valido informando todos os campos."""
        payload = {
            "username": "novo_usuario",
            "nome_completo": "Novo Usuario",
            "password": "SenhaForte123!",
            "matricula": "20260001",
            "tipo": "OR",
        }
        request = self.factory.post(
            "/api/usuarios/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        response = self.view(request)
        dados = json.loads(response.content)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(dados["username"], "novo_usuario")
        self.assertEqual(dados["tipo"], "OR")
        self.assertTrue(Usuario.objects.filter(username="novo_usuario").exists())

    def test_post_cria_usuario_sem_tipo_usa_padrao_aluno(self) -> None:
        """Quando 'tipo' nao e informado, o padrao ALUNO deve ser usado."""
        payload = {
            "username": "usuario_sem_tipo",
            "nome_completo": "Usuario Sem Tipo",
            "password": "SenhaForte123!",
        }
        request = self.factory.post(
            "/api/usuarios/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        response = self.view(request)
        dados = json.loads(response.content)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(dados["tipo"], "AL")

    def test_post_tipo_invalido_retorna_400(self) -> None:
        """Um tipo de perfil invalido deve ser rejeitado com 400."""
        payload = {
            "username": "usuario_tipo_invalido",
            "nome_completo": "Usuario Invalido",
            "password": "SenhaForte123!",
            "tipo": "XX",
        }
        request = self.factory.post(
            "/api/usuarios/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        response = self.view(request)
        dados = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertIn("Tipo invalido", dados["error"])
        self.assertFalse(
            Usuario.objects.filter(username="usuario_tipo_invalido").exists()
        )

    def test_post_campo_obrigatorio_ausente_retorna_400(self) -> None:
        """A ausencia de um campo obrigatorio (ex: password) deve retornar 400."""
        payload = {
            "username": "usuario_incompleto",
            "nome_completo": "Usuario Incompleto",
            # 'password' ausente de proposito
        }
        request = self.factory.post(
            "/api/usuarios/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        response = self.view(request)
        dados = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertIn("Campo obrigatorio ausente", dados["error"])

    def test_post_corpo_invalido_retorna_400(self) -> None:
        """Um corpo de requisicao que nao e JSON valido deve cair no except generico."""
        request = self.factory.post(
            "/api/usuarios/",
            data="isto nao e um json",
            content_type="application/json",
        )
        response = self.view(request)

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", json.loads(response.content))


class UsuarioDetalheControllerTestCase(TestCase):
    """Testes para a view de detalhe/atualizacao/remocao (UsuarioDetalheController)."""

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.view = UsuarioDetalheController.as_view()
        self.usuario = Usuario.objects.create_user(
            username="usuario_detalhe",
            email="detalhe@test.com",
            password="SenhaForte123!",
            nome_completo="Usuario Detalhe",
            tipo="AL",
        )

    # --- GET ---

    def test_get_usuario_existente(self) -> None:
        """Retorna 200 e os dados do usuario quando o ID existe."""
        request = self.factory.get(f"/api/usuarios/{self.usuario.id}/")
        response = self.view(request, usuario_id=str(self.usuario.id))
        dados = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(dados["username"], "usuario_detalhe")

    def test_get_usuario_inexistente_retorna_404(self) -> None:
        """Retorna 404 quando o UUID e valido mas nao corresponde a nenhum usuario."""
        request = self.factory.get(f"/api/usuarios/{uuid.uuid4()}/")
        response = self.view(request, usuario_id=str(uuid.uuid4()))

        self.assertEqual(response.status_code, 404)

    def test_get_usuario_id_malformado_retorna_404(self) -> None:
        """Um ID que nao e um UUID valido deve ser tratado como nao encontrado."""
        request = self.factory.get("/api/usuarios/id-invalido/")
        response = self.view(request, usuario_id="id-invalido")

        self.assertEqual(response.status_code, 404)

    # --- PUT ---

    def test_put_atualiza_usuario_com_sucesso(self) -> None:
        """Atualiza campos permitidos de um usuario existente."""
        payload = {"nome_completo": "Nome Atualizado", "matricula": "999", "tipo": "GE"}
        request = self.factory.put(
            f"/api/usuarios/{self.usuario.id}/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        response = self.view(request, usuario_id=str(self.usuario.id))
        dados = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(dados["nome_completo"], "Nome Atualizado")
        self.assertEqual(dados["matricula"], "999")
        self.assertEqual(dados["tipo"], "GE")

        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.nome_completo, "Nome Atualizado")

    def test_put_usuario_inexistente_retorna_404(self) -> None:
        """Atualizar um usuario inexistente deve retornar 404."""
        payload = {"nome_completo": "Nao importa"}
        request = self.factory.put(
            f"/api/usuarios/{uuid.uuid4()}/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        response = self.view(request, usuario_id=str(uuid.uuid4()))

        self.assertEqual(response.status_code, 404)

    def test_put_tipo_invalido_retorna_400(self) -> None:
        """Um tipo de perfil invalido na atualizacao deve retornar 400."""
        payload = {"tipo": "ZZ"}
        request = self.factory.put(
            f"/api/usuarios/{self.usuario.id}/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        response = self.view(request, usuario_id=str(self.usuario.id))
        dados = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertIn("Tipo invalido", dados["error"])

    def test_put_corpo_invalido_retorna_400(self) -> None:
        """Um corpo de requisicao invalido no PUT deve cair no except generico."""
        request = self.factory.put(
            f"/api/usuarios/{self.usuario.id}/",
            data="isto nao e um json",
            content_type="application/json",
        )
        response = self.view(request, usuario_id=str(self.usuario.id))

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", json.loads(response.content))

    # --- DELETE ---

    def test_delete_desativa_usuario_existente(self) -> None:
        """Remove (soft delete) um usuario existente, desativando-o."""
        request = self.factory.delete(f"/api/usuarios/{self.usuario.id}/")
        response = self.view(request, usuario_id=str(self.usuario.id))
        dados = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertIn("mensagem", dados)

        self.usuario.refresh_from_db()
        self.assertFalse(self.usuario.is_active)

    def test_delete_usuario_inexistente_retorna_404(self) -> None:
        """Remover um usuario inexistente deve retornar 404."""
        request = self.factory.delete(f"/api/usuarios/{uuid.uuid4()}/")
        response = self.view(request, usuario_id=str(uuid.uuid4()))

        self.assertEqual(response.status_code, 404)
