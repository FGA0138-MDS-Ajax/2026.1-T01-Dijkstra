"""apps.security.controllers.usuario_controller - Controller HTTP para Usuarios."""

from __future__ import annotations

import json

try:
    from typing import Self
except ImportError:
    from typing import TypeVar
    Self = TypeVar("Self")  # type: ignore[assignment]

from django.http import JsonResponse, HttpRequest
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from apps.security.models import Usuario

__version__ = "0.1.0"
__license__ = "AGPL V3"


@method_decorator(csrf_exempt, name="dispatch")
class UsuarioController(View):
    """Controller para gerenciar requisicoes de Usuarios."""

    def get(self, request: HttpRequest, usuario_id: str = None) -> JsonResponse:
        """Lista todos os usuarios ou retorna um especifico."""
        if usuario_id:
            try:
                usuario = Usuario.objects.get(pk=usuario_id)
                return JsonResponse(self._serialize(usuario))
            except Usuario.DoesNotExist:
                return JsonResponse({"error": "Usuario nao encontrado"}, status=404)
        usuarios = list(Usuario.objects.values(
            "id", "email", "nome_completo", "matricula", "tipo", "is_active"
        ))
        return JsonResponse(usuarios, safe=False)

    def post(self, request: HttpRequest) -> JsonResponse:
        """Cria um novo usuario. Body JSON com campos do usuario + password."""
        try:
            data = json.loads(request.body)
            password = data.pop("password", None)
            usuario = Usuario(**data)
            if password:
                usuario.set_password(password)
            usuario.full_clean()
            usuario.save()
            return JsonResponse(self._serialize(usuario), status=201)
        except Exception as e:  # pylint: disable=broad-exception-caught
            return JsonResponse({"error": str(e)}, status=400)

    def put(self, request: HttpRequest, usuario_id: str) -> JsonResponse:
        """Atualiza um usuario existente."""
        try:
            usuario = Usuario.objects.get(pk=usuario_id)
            data = json.loads(request.body)
            for field, value in data.items():
                setattr(usuario, field, value)
            usuario.full_clean()
            usuario.save()
            return JsonResponse(self._serialize(usuario))
        except Usuario.DoesNotExist:
            return JsonResponse({"error": "Usuario nao encontrado"}, status=404)
        except Exception as e:  # pylint: disable=broad-exception-caught
            return JsonResponse({"error": str(e)}, status=400)

    def delete(self, request: HttpRequest, usuario_id: str) -> JsonResponse:
        """Deleta um usuario pelo ID."""
        try:
            usuario = Usuario.objects.get(pk=usuario_id)
            usuario.delete()
            return JsonResponse({"message": "Usuario deletado com sucesso"}, status=204)
        except Usuario.DoesNotExist:
            return JsonResponse({"error": "Usuario nao encontrado"}, status=404)

    def _serialize(self, usuario: Usuario) -> dict:
        """Serializa Usuario para dicionario."""
        return {
            "id": str(usuario.id),
            "email": usuario.email,
            "nome_completo": usuario.nome_completo,
            "matricula": usuario.matricula,
            "tipo": usuario.tipo,
            "is_active": usuario.is_active,
            "foto": usuario.foto.url if usuario.foto and hasattr(usuario.foto, "url") else None,
        }
