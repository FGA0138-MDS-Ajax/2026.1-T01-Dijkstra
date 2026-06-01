"""
apps.core.controllers.eventos_controller
=========================================
Controller HTTP para o domínio de Eventos.

Componentes Principais
----------------------
- :class:`EventosController`: View Django que expõe os endpoints REST de Eventos,
  delegando a lógica ao :class:`~apps.core.services.eventos_service.EventosService`.
- :func:`event_list_controller`: view Django que renderiza a listagem de eventos
  com suporte a filtro por intervalo de datas.

Notas
-----
- Requer Python >= 3.12
- Criado por `MontMarcos <https://github.com/MontMarcos>`_ em 26 maio 2026
- Lint e testes por `Saresu <https://github.com/Saresu>`_ em 28 maio 2026
- Revisado por `Gui-fga <https://github.com/Gui-fga>`_ em 30 maio 2026
- Revisado por `Saresu <https://github.com/Saresu>`_ em 30 maio 2026
"""

from __future__ import annotations

import json

from typing import Self

from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.core.paginator import Paginator
from apps.core.services.eventos_service import EventosService
from apps.core.forms import DateFilterForm

__version__ = "0.0.3"
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

    def get(self: Self, request: HttpRequest) -> JsonResponse | HttpResponse:
        """
        Lista todos os eventos.

        :param request: Objeto da requisição HTTP.
        :type request: HttpRequest
        :returns: JsonResponse ou HttpResponse com a lista de eventos.
        :rtype: JsonResponse | HttpResponse
        """

        eventos = self.service.listar_eventos()
        if request.headers.get("Accept") == "application/json":
            return JsonResponse([self._serialize_evento(e) for e in eventos], safe=False)
        return render(request, "core/event_list.html", {"eventos": eventos})

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
            "gestor": evento.gestor,
            "criado_em": format_field(evento.criado_em),
            "atualizado_em": format_field(evento.atualizado_em),
            "imagem": evento.imagem.url
            if evento.imagem and hasattr(evento.imagem, "url")
            else None,
        }


# usa-se todo com a faser para o pylint nao reclamar do codigo
# a fazer: nao seria o caso de reanalisar toda a classe para integrar
# essa funcao como um metodo?
def event_list_controller(request):
    """
    Renderiza a listagem de eventos com suporte a filtro por intervalo de datas.

    :param request: Objeto da requisição HTTP.
    :type request: HttpRequest
    :returns: Resposta HTTP com o template ``core/event_list.html``, o formulário
              de filtro e a lista de eventos filtrados.
    :rtype: HttpResponse
    """
    form = DateFilterForm(request.GET)
    service = EventosService()

    data_inicio = None
    data_fim = None

    if form.is_valid():
        data_inicio = form.cleaned_data.get("data_inicio")
        data_fim = form.cleaned_data.get("data_fim")

    events = service.get_filtered_events(data_inicio=data_inicio, data_fim=data_fim)

    paginator = Paginator(events, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "core/event_list.html",
        {
            "form": form,
            "page_obj": page_obj,
        },
    )


def detalhes_evento(request, evento_id):
    """
    Exibe os detalhes de um evento específico.
    """
    service = EventosService()

    evento = service.buscar_evento(evento_id)

    return render(
        request,
        "core/detalhes_evento.html",
        {
            "evento": evento
        }
    )
