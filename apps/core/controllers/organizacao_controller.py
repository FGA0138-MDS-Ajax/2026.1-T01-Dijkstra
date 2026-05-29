"""apps.core.controllers.organizacao_controller - Controller HTTP para Organizacoes."""

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

from apps.core.models import Organizacao

__version__ = "0.1.0"
__license__ = "AGPL V3"


@method_decorator(csrf_exempt, name="dispatch")
class OrganizacaoController(View):
    """Controller para gerenciar requisicoes de Organizacoes."""

    def get(self, request: HttpRequest, org_id: str = None) -> JsonResponse:
        """Lista todas as organizacoes ou retorna uma especifica."""
        if org_id:
            try:
                org = Organizacao.objects.get(pk=org_id)
                return JsonResponse(self._serialize(org))
            except Organizacao.DoesNotExist:
                return JsonResponse({"error": "Organizacao nao encontrada"}, status=404)
        orgs = [self._serialize(o) for o in Organizacao.objects.all()]
        return JsonResponse(orgs, safe=False)

    def post(self, request: HttpRequest) -> JsonResponse:
        """Cria uma nova organizacao."""
        try:
            if request.content_type == "application/json":
                data = json.loads(request.body)
            else:
                data = request.POST.dict()
                if request.FILES.get("foto"):
                    data["foto"] = request.FILES["foto"]
            membros_ids = data.pop("membros", [])
            org = Organizacao.objects.create(**data)
            if membros_ids:
                org.membros.set(membros_ids)
            return JsonResponse(self._serialize(org), status=201)
        except Exception as e:  # pylint: disable=broad-exception-caught
            return JsonResponse({"error": str(e)}, status=400)

    def put(self, request: HttpRequest, org_id: str) -> JsonResponse:
        """Atualiza uma organizacao existente."""
        try:
            org = Organizacao.objects.get(pk=org_id)
            data = json.loads(request.body)
            membros_ids = data.pop("membros", None)
            for field, value in data.items():
                setattr(org, field, value)
            org.save()
            if membros_ids is not None:
                org.membros.set(membros_ids)
            return JsonResponse(self._serialize(org))
        except Organizacao.DoesNotExist:
            return JsonResponse({"error": "Organizacao nao encontrada"}, status=404)
        except Exception as e:  # pylint: disable=broad-exception-caught
            return JsonResponse({"error": str(e)}, status=400)

    def delete(self, request: HttpRequest, org_id: str) -> JsonResponse:
        """Deleta uma organizacao pelo ID."""
        try:
            org = Organizacao.objects.get(pk=org_id)
            org.delete()
            return JsonResponse({"message": "Organizacao deletada com sucesso"}, status=204)
        except Organizacao.DoesNotExist:
            return JsonResponse({"error": "Organizacao nao encontrada"}, status=404)

    def _serialize(self, org: Organizacao) -> dict:
        """Serializa Organizacao para dicionario."""
        return {
            "id": str(org.id),
            "nome": org.nome,
            "descricao": org.descricao,
            "foto": org.foto.url if org.foto and hasattr(org.foto, "url") else None,
            "membros": [str(m.id) for m in org.membros.all()],
        }
