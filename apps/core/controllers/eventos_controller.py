"""
apps.core.controllers.eventos_controller
=========================================
Controller HTTP para o domínio de Eventos.

Componentes Principais
----------------------
- :class:`EventosController`: View Django que expõe os endpoints REST de Eventos,
  delegando a lógica ao :class:`~apps.core.services.eventos_service.EventosService`.

Notas
-----
- Requer Python >= 3.12
- Criado por `MontMarcos <https://github.com/MontMarcos>`_ em 26 maio 2026
- Lint e testes por `Saresu <https://github.com/Saresu>`_ em 28 maio 2026
- Atualização de controller por `Welder60 <https://github.com/Welder60>`_ em 29 maio 2026
"""

# compatibilidade
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

from apps.core.models import Evento

__version__ = "0.1.0"
__license__ = "AGPL V3"


@method_decorator(csrf_exempt, name="dispatch")
class EventosController(View):
    """Controller para gerenciar requisicoes de Eventos."""

    def get(self, request: HttpRequest, evento_id: str = None) -> JsonResponse:
        """Lista todos os eventos ou retorna um especifico."""
        if evento_id:
            try:
                evento = Evento.objects.get(pk=evento_id)
                return JsonResponse(self._serialize(evento))
            except Evento.DoesNotExist:
                return JsonResponse({"error": "Evento nao encontrado"}, status=404)
        eventos = [
            self._serialize(e)
            for e in Evento.objects.select_related("organizador", "organizacao")
        ]
        return JsonResponse(eventos, safe=False)

    def post(self, request: HttpRequest) -> JsonResponse:
        """Cria um novo evento."""
        try:
            if request.content_type == "application/json":
                data = json.loads(request.body)
            else:
                data = request.POST.dict()
                if request.FILES.get("foto"):
                    data["foto"] = request.FILES["foto"]
            evento = Evento.objects.create(**data)
            return JsonResponse(self._serialize(evento), status=201)
        except Exception as e:  # pylint: disable=broad-exception-caught
            return JsonResponse({"error": str(e)}, status=400)

    def put(self, request: HttpRequest, evento_id: str) -> JsonResponse:
        """Atualiza um evento existente."""
        try:
            evento = Evento.objects.get(pk=evento_id)
            data = json.loads(request.body)
            for field, value in data.items():
                setattr(evento, field, value)
            evento.save()
            return JsonResponse(self._serialize(evento))
        except Evento.DoesNotExist:
            return JsonResponse({"error": "Evento nao encontrado"}, status=404)
        except Exception as e:  # pylint: disable=broad-exception-caught
            return JsonResponse({"error": str(e)}, status=400)

    def delete(self, request: HttpRequest, evento_id: str) -> JsonResponse:
        """Deleta um evento pelo ID."""
        try:
            evento = Evento.objects.get(pk=evento_id)
            evento.delete()
            return JsonResponse({"message": "Evento deletado com sucesso"}, status=204)
        except Evento.DoesNotExist:
            return JsonResponse({"error": "Evento nao encontrado"}, status=404)

    def _serialize(self, evento: Evento) -> dict:
        """Serializa Evento para dicionario."""
        return {
            "id": str(evento.id),
            "titulo": evento.titulo,
            "descricao": evento.descricao,
            "data_realizacao": evento.data_realizacao.isoformat(),
            "criado_em": evento.criado_em.isoformat(),
            "organizador": str(evento.organizador_id),
            "organizacao": str(evento.organizacao_id),
            "foto": evento.foto.url if evento.foto and hasattr(evento.foto, "url") else None,
        }
