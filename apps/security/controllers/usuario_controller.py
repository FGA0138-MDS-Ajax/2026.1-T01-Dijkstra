"""Controller HTTP para o dominio de Usuarios.

apps.security.controllers.usuario_controller
apps.security.controllers.usuario_controller
=============================================
Controller HTTP para o dominio de Usuarios.

Componentes Principais
----------------------
- :class:`UsuarioController`: View Django que expoe os endpoints REST de
  Usuarios (listagem e criacao).
- :class:`UsuarioDetalheController`: View Django para operacoes em um
  usuario especifico (busca, atualizacao e exclusao).

Notas
-----
- Requer Python >= 3.12
"""

from __future__ import annotations

import json
import uuid
from typing import Self

from django.contrib.auth.hashers import make_password
from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from apps.security.models.usuario_models import TipoPerfil, Usuario

__version__ = "0.0.1"
__license__ = "AGPL V3"


def _serialize_usuario(usuario: Usuario) -> dict:
    """
    Serializa uma instancia de Usuario para dicionario JSON-serializavel.

    :param usuario: Instancia do usuario a ser serializada.
    :type usuario: Usuario
    :returns: Dicionario com os campos publicos do usuario.
    :rtype: dict
    """
    return {
        "id": str(usuario.id),
        "username": usuario.username,
        "nome_completo": usuario.nome_completo,
        "matricula": usuario.matricula,
        "tipo": usuario.tipo,
        "is_active": usuario.is_active,
        "is_aluno": usuario.is_aluno,
        "is_organizador": usuario.is_organizador,
        "is_gestor": usuario.is_gestor,
    }


@method_decorator(csrf_exempt, name="dispatch")
class UsuarioController(View):
    """Controller para listagem e criacao de Usuarios."""

    def get(self: Self, request: HttpRequest) -> JsonResponse:
        """
        Lista todos os usuarios cadastrados.

        :param request: Objeto da requisicao HTTP.
        :type request: HttpRequest
        :returns: JsonResponse com a lista de usuarios.
        :rtype: JsonResponse
        """
        usuarios = Usuario.objects.all()
        return JsonResponse(
            [_serialize_usuario(u) for u in usuarios],
            safe=False,
        )

    def post(self: Self, request: HttpRequest) -> JsonResponse:
        """
        Cria um novo usuario.

        Campos esperados no body JSON:
        - username (str, obrigatorio)
        - nome_completo (str, obrigatorio)
        - password (str, obrigatorio)
        - matricula (str, opcional)
        - tipo (str, opcional — valores: AL, OR, GE, AD; padrao: AL)

        :param request: Objeto da requisicao HTTP com dados do usuario.
        :type request: HttpRequest
        :returns: JsonResponse com o usuario criado (201) ou erro (400).
        :rtype: JsonResponse
        """
        try:
            data = json.loads(request.body)

            tipo = data.get("tipo", TipoPerfil.ALUNO)
            if tipo not in TipoPerfil.values:
                return JsonResponse(
                    {"error": f"Tipo invalido. Escolha entre: {TipoPerfil.values}"},
                    status=400,
                )

            usuario = Usuario.objects.create(
                username=data["username"],
                nome_completo=data["nome_completo"],
                password=make_password(data["password"]),
                matricula=data.get("matricula"),
                tipo=tipo,
            )
            return JsonResponse(_serialize_usuario(usuario), status=201)

        except KeyError as e:
            return JsonResponse({"error": f"Campo obrigatorio ausente: {e}"}, status=400)
        except Exception as e:  # pylint: disable=broad-exception-caught
            return JsonResponse({"error": str(e)}, status=400)


@method_decorator(csrf_exempt, name="dispatch")
class UsuarioDetalheController(View):
    """Controller para operacoes em um Usuario especifico."""

    def _get_usuario(self: Self, usuario_id: str) -> Usuario | None:
        """
        Busca um usuario pelo ID.

        :param usuario_id: UUID do usuario em formato string.
        :type usuario_id: str
        :returns: Instancia do usuario ou None se nao encontrado.
        :rtype: Usuario or None
        """
        try:
            return Usuario.objects.get(id=uuid.UUID(usuario_id))
        except (Usuario.DoesNotExist, ValueError):
            return None

    def get(self: Self, request: HttpRequest, usuario_id: str) -> JsonResponse:
        """
        Retorna os dados de um usuario especifico.

        :param request: Objeto da requisicao HTTP.
        :type request: HttpRequest
        :param usuario_id: UUID do usuario.
        :type usuario_id: str
        :returns: JsonResponse com os dados do usuario (200) ou erro (404).
        :rtype: JsonResponse
        """
        usuario = self._get_usuario(usuario_id)
        if not usuario:
            return JsonResponse({"error": "Usuario nao encontrado."}, status=404)
        return JsonResponse(_serialize_usuario(usuario))

    def put(self: Self, request: HttpRequest, usuario_id: str) -> JsonResponse:
        """
        Atualiza os dados de um usuario existente.

        Campos aceitos no body JSON: nome_completo, matricula, tipo, is_active.

        :param request: Objeto da requisicao HTTP com os campos a atualizar.
        :type request: HttpRequest
        :param usuario_id: UUID do usuario.
        :type usuario_id: str
        :returns: JsonResponse com o usuario atualizado (200) ou erro (400/404).
        :rtype: JsonResponse
        """
        usuario = self._get_usuario(usuario_id)
        if not usuario:
            return JsonResponse({"error": "Usuario nao encontrado."}, status=404)

        try:
            data = json.loads(request.body)
            campos_permitidos = {"nome_completo", "matricula", "tipo", "is_active"}

            if "tipo" in data and data["tipo"] not in TipoPerfil.values:
                return JsonResponse(
                    {"error": f"Tipo invalido. Escolha entre: {TipoPerfil.values}"},
                    status=400,
                )

            for campo in campos_permitidos:
                if campo in data:
                    setattr(usuario, campo, data[campo])

            usuario.save()
            return JsonResponse(_serialize_usuario(usuario))

        except Exception as e:  # pylint: disable=broad-exception-caught
            return JsonResponse({"error": str(e)}, status=400)

    def delete(self: Self, request: HttpRequest, usuario_id: str) -> JsonResponse:
        """
        Desativa (soft delete) um usuario pelo seu ID.

        :param request: Objeto da requisicao HTTP.
        :type request: HttpRequest
        :param usuario_id: UUID do usuario.
        :type usuario_id: str
        :returns: JsonResponse com confirmacao (200) ou erro (404).
        :rtype: JsonResponse
        """
        usuario = self._get_usuario(usuario_id)
        if not usuario:
            return JsonResponse({"error": "Usuario nao encontrado."}, status=404)

        usuario.is_active = False
        usuario.save()
        return JsonResponse({"mensagem": "Usuario desativado com sucesso."})
