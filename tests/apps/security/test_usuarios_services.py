"""
tests.apps.security.services.test_usuarios_services
===================================================
Testes de unidade e integracao para a camada de Service e Repository de Usuarios.
"""

import uuid
from django.test import TestCase

# from apps.security.models.usuario_models import Usuario
from apps.security.repositories.usuarios_repositories import UsuarioRepository
from apps.security.services.usuarios_services import UsuarioService


class UsuarioServiceAndRepositoryTestCase(TestCase):
    """Garante a cobertura total dos metodos existentes de UsuarioService e UsuarioRepository."""

    def setUp(self) -> None:
        """Inicializa as instancias do servico e do repositorio."""
        self.service = UsuarioService()
        self.repository = UsuarioRepository()
        self.dados_base = {
            "username": "dijkstra_test",
            "email": "dijkstra@teste.com",
            "nome_completo": "Edsger Dijkstra",
            "tipo": "AL",
        }

    def test_inicializacao_service(self) -> None:
        """Garante que a service inicializa corretamente o repositorio."""
        self.assertIsNotNone(self.service.repository)
        self.assertIsInstance(self.service.repository, UsuarioRepository)

    def test_fluxo_crud_completo_repository(self) -> None:
        """Testa as operacoes CRUD expostas diretamente pelo repositorio."""

        usuario = self.repository.create_usuario(self.dados_base)
        self.assertIsNotNone(usuario.pk)
        self.assertEqual(usuario.username, "dijkstra_test")

        usuario_buscado = self.repository.get_usuario_by_id(usuario.pk)
        self.assertEqual(usuario_buscado, usuario)

        usuario_invalido = self.repository.get_usuario_by_id(uuid.uuid4())
        self.assertIsNone(usuario_invalido)

        todos = self.repository.get_all_usuarios()
        self.assertIn(usuario, todos)

        novos_dados = {"nome_completo": "Edsger W. Dijkstra"}
        usuario_atualizado = self.repository.update_usuario(usuario.pk, novos_dados)
        self.assertIsNotNone(usuario_atualizado)
        if usuario_atualizado:
            self.assertEqual(usuario_atualizado.nome_completo, "Edsger W. Dijkstra")

        atualizacao_invalida = self.repository.update_usuario(uuid.uuid4(), novos_dados)
        self.assertIsNone(atualizacao_invalida)

        removido = self.repository.delete_usuario(usuario.pk)
        self.assertTrue(removido)

        remocao_invalida = self.repository.delete_usuario(uuid.uuid4())
        self.assertFalse(remocao_invalida)

    def test_get_organizadores_usuarios(self) -> None:
        """Garante que a listagem de organizadores filtra os usuarios corretamente no repository."""
        self.repository.create_usuario(
            {"username": "aluno_perfil", "nome_completo": "Perfil Aluno", "tipo": "AL"}
        )
        organizador = self.repository.create_usuario(
            {
                "username": "org_perfil",
                "nome_completo": "Perfil Organizador",
                "tipo": "OR",
            }
        )

        organizadores = list(self.repository.get_organizadores_usuarios())

        self.assertIn(organizador, organizadores)
        for org in organizadores:
            self.assertEqual(org.tipo, "OR")
