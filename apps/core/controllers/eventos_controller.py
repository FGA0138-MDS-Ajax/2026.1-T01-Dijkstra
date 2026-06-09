"""Controller HTTP para o dominio de Eventos.

apps.core.controllers.eventos_controller
apps.core.controllers.eventos_controller
=========================================
Controller HTTP para o dominio de Eventos.

Componentes Principais
----------------------
- :class:`EventosController`: View Django que expoe os endpoints REST de
  Eventos, delegando a logica ao
  :class:`~apps.core.services.eventos_service.EventosService`.
- :func:`event_list_controller`: view Django que renderiza a listagem de
  eventos com suporte a filtro por intervalo de datas.

Notas
-----
- Requer Python >= 3.12
- Criado por `MontMarcos <https://github.com/MontMarcos>`_ em 26 maio 2026
- Lint e testes por `Saresu <https://github.com/Saresu>`_ em 28 maio 2026
- Revisado por `Gui-fga <https://github.com/Gui-fga>`_ em 30 maio 2026
- Revisado por `Saresu <https://github.com/Saresu>`_ em 30 maio 2026
- Alterado por `DaviiGualbertoo <https://github.com/DaviiGualbertoo>`_ em 08 junho 2026
"""

from __future__ import annotations

import json
from typing import Self

from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from apps.core.forms import DateFilterForm
from apps.core.services.eventos_service import EventosService
from apps.core.models.inscricao_models import Inscricao

__version__ = "0.0.4"
__license__ = "AGPL V3"


@method_decorator(csrf_exempt, name="dispatch")
class EventosController(View):
    """Controller para gerenciar requisicoes de Eventos."""

    def __init__(self: Self, **kwargs):
        """Inicializa o controller com uma instancia do servico de eventos."""
        super().__init__(**kwargs)
        self.service = EventosService()

    def get(self: Self, request: HttpRequest) -> JsonResponse | HttpResponse:
        """
        Lista todos os eventos publicados.

        :param request: Objeto da requisicao HTTP.
        :type request: HttpRequest
        :returns: JsonResponse ou HttpResponse com a lista de eventos.
        :rtype: JsonResponse | HttpResponse
        """
        eventos = self.service.listar_eventos_publicados()
        if request.headers.get("Accept") == "application/json":
            return JsonResponse(
                [self._serialize_evento(e) for e in eventos], safe=False
            )
        return render(request, "core/event_list.html", {"eventos": eventos})

    def post(self: Self, request: HttpRequest) -> JsonResponse:
        """
        Cria um novo evento.

        :param request: Objeto da requisicao HTTP com dados do evento no body.
        :type request: HttpRequest
        :returns: JsonResponse com o evento criado (201) ou erro (400).
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
        except Exception as e:  # pylint: disable=broad-exception-caught
            return JsonResponse({"error": str(e)}, status=400)

    def _serialize_evento(self: Self, evento) -> dict:
        """
        Serializa uma instancia de Evento para dicionario JSON-serializavel.

        :param evento: Instancia do evento a ser serializada.
        :type evento: Evento
        :returns: Dicionario com os campos do evento.
        :rtype: dict
        """

        def format_field(field):
            """Formata campo para ISO ou retorna o valor bruto."""
            if hasattr(field, "isoformat"):
                return field.isoformat()
            return field

        return {
            "id": str(evento.id),
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
            "imagem": (
                evento.imagem.url
                if evento.imagem and hasattr(evento.imagem, "url")
                else None
            ),
        }


def event_list_controller(request):
    """
    Renderiza a listagem de eventos com suporte a filtro por data.

    :param request: Objeto da requisicao HTTP.
    :type request: HttpRequest
    :returns:
        Resposta HTTP com o template ``core/event_list.html``, o formulario
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

    events = service.get_filtered_events(
        data_inicio=data_inicio, data_fim=data_fim
    )

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
    Exibe os detalhes de um evento especifico.

    :param request: Objeto da requisicao HTTP.
    :type request: HttpRequest
    :param evento_id: UUID do evento a ser exibido.
    :type evento_id: uuid.UUID
    :returns: Resposta HTTP com o template ``core/detalhes_evento.html``.
    :rtype: HttpResponse
    """
    service = EventosService()
    evento = service.buscar_evento(evento_id)

    inscricao = None
    if request.user.is_authenticated:
        inscricao = Inscricao.objects.filter(aluno=request.user, evento=evento).first()

    evento.vagas_ocupadas = Inscricao.objects.filter(evento=evento).exclude(
        status__in=[Inscricao.Status.CANCELADA, Inscricao.Status.REJEITADA]
    ).count()


    return render(
        request,
        "core/detalhes_evento.html",
        {
            "evento": evento,
            "inscricao": inscricao,
        },
    )