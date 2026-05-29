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
"""

# compatibilidade
from __future__ import annotations

import json

from typing import Self

from django.http import JsonResponse, HttpRequest
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from apps.core.services.eventos_service import EventosService

__version__ = "0.0.2"
__license__ = "AGPL V3"


@method_decorator(csrf_exempt, name="dispatch")
class EventosController(View):
    """Controller para gerenciar requisições de Eventos."""

    def __init__(self: Self, **kwargs):
        """
        Inicializa o controller com uma instância do serviço de eventos.
        """

        super().__init__(**kwargs)
        self.service = EventosService()

    # request causa erro por nao ser utilizado no metodo suprimido por hora para
    # passar limpo no lint
    # a fazer: Rever uso da assinatura do metodo
    # refeito vide g
    # def get(self: Self, evento_id: int = None) -> JsonResponse:
    def get(self: Self, request: HttpRequest, evento_id: int = None) -> JsonResponse:
        """
        Lista todos os eventos ou retorna um evento específico.

        :param request: Objeto da requisição HTTP.
        :type request: HttpRequest
        :param evento_id: ID do evento (opcional). Se informado, retorna apenas esse evento.
        :type evento_id: int or None
        :returns: JsonResponse com um evento ou lista de eventos.
        :rtype: JsonResponse
        """

        if evento_id:
            evento = self.service.buscar_evento(evento_id)
            if not evento:
                return JsonResponse({"error": "Evento não encontrado"}, status=404)
            return JsonResponse(self._serialize_evento(evento))

        eventos = self.service.listar_eventos()
        return JsonResponse([self._serialize_evento(e) for e in eventos], safe=False)

    def post(self: Self, request: HttpRequest) -> JsonResponse:
        """
        Cria um novo evento.

        :param request: Objeto da requisição HTTP com dados do evento no body.
        :type request: HttpRequest
        :returns: JsonResponse com o evento criado (status 201) ou erro (status 400).
        :rtype: JsonResponse
        """

        try:
            if request.content_type == "application/json":
                data = json.loads(request.body)
                evento = self.service.criar_evento(data)
            else:
                data = request.POST.dict()
                if request.FILES.get("imagem"):
                    data["imagem"] = request.FILES["imagem"]
                evento = self.service.criar_evento(data)

            return JsonResponse(self._serialize_evento(evento), status=201)
        # erro de captura geral de erro. reavaliar para capturar realmente
        # o erro especifico e tratar de acorodo.
        # a fazer granularizar Exception
        except Exception as e:  # pylint: disable=broad-exception-caught
            return JsonResponse({"error": str(e)}, status=400)

    def put(self: Self, request: HttpRequest, evento_id: int) -> JsonResponse:
        """
        Atualiza um evento existente.

        :param request: Objeto da requisição HTTP com os dados a atualizar no body.
        :type request: HttpRequest
        :param evento_id: ID do evento a ser atualizado.
        :type evento_id: int
        :returns: JsonResponse com o evento atualizado ou erro (status 400/404).
        :rtype: JsonResponse
        """
        try:
            data = json.loads(request.body)
            evento = self.service.atualizar_evento(evento_id, data)
            if not evento:
                return JsonResponse({"error": "Evento não encontrado"}, status=404)
            return JsonResponse(self._serialize_evento(evento))
        # erro de captura geral de erro. reavaliar para capturar realmente
        # o erro especifico e tratar de acorodo.
        # a fazer granularizar Exception
        except Exception as e:  # pylint: disable=broad-exception-caught
            return JsonResponse({"error": str(e)}, status=400)

    # request causa erro por nao ser utilizado no metodo suprimido por hora para
    # passar limpo no lint
    # a fazer: Rever uso da assinatura do metodo
    # def delete(self: Self, evento_id: int) -> JsonResponse:
    # quebra o django pela assinatura, revertido para chamada original suprimindo
    # erro anterior erra elevado pelo uso de estrutura atual de MVC.
    def delete(self: Self, request: HttpRequest, evento_id: int) -> JsonResponse:
        """
        Deleta um evento pelo ID.

        :param request: Objeto da requisição HTTP.
        :type request: HttpRequest
        :param evento_id: ID do evento a ser deletado.
        :type evento_id: int
        :returns: JsonResponse com mensagem de sucesso (status 204) ou erro (status 404).
        :rtype: JsonResponse
        """
        success = self.service.excluir_evento(evento_id)
        if not success:
            return JsonResponse({"error": "Evento não encontrado"}, status=404)
        return JsonResponse({"message": "Evento deletado com sucesso"}, status=204)

    def _serialize_evento(self: Self, evento) -> dict:
        """
        Serializa uma instância de Evento para dicionário JSON-serializável.

        :param evento: Instância do evento a ser serializada.
        :type evento: Evento
        :returns: Dicionário com os campos do evento.
        :rtype: dict
        """

        def format_field(field):
            if hasattr(field, "isoformat"):
                return field.isoformat()
            return field

        return {
            "id": evento.id,
            "nome": evento.nome,
            "data": format_field(evento.data),
            "horario": format_field(evento.horario),
            "local": evento.local,
            "organizador": evento.organizador,
            "descricao": evento.descricao,
            "capacidade": evento.capacidade,
            "criado_em": format_field(evento.criado_em),
            "atualizado_em": format_field(evento.atualizado_em),
            "imagem": evento.imagem.url
            if evento.imagem and hasattr(evento.imagem, "url")
            else None,
        }
