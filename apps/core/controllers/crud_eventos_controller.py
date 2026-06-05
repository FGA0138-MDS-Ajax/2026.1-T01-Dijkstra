"""Controller HTTP para gestão (CRUD) de Eventos.

apps.core.controllers.crud_eventos_controller
==============================================
Views de gerenciamento de eventos — listagem com filtros, criação,
detalhe, edição e exclusão.

Estas rotas são exclusivas para gestão e não se confundem com a
página inicial pública, que é apenas de consulta.

Notas
-----
- Requer Python >= 3.12
"""

from __future__ import annotations

import uuid

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from apps.core.forms import EventoForm
from apps.core.models.eventos_models import Evento
from apps.core.services.eventos_service import EventosService

__version__ = "0.0.1"
__license__ = "AGPL V3"

_service = EventosService()


@login_required
@require_http_methods(["GET"])
def gestao_eventos_list(request: HttpRequest) -> HttpResponse:
    """
    Lista todos os eventos para gestão, com filtro por status.

    :param request: Objeto da requisição HTTP.
    :type request: HttpRequest
    :returns: Página HTML com a listagem de eventos.
    :rtype: HttpResponse
    """
    status_filtro = request.GET.get("status", "")
    eventos = Evento.objects.all()
    if status_filtro:
        eventos = eventos.filter(status=status_filtro)
    return render(
        request,
        "core/eventos/list.html",
        {"eventos": eventos, "status_filtro": status_filtro},
    )


@login_required
@require_http_methods(["GET", "POST"])
def gestao_evento_novo(request: HttpRequest) -> HttpResponse:
    """
    Exibe o formulário de criação de evento e processa o envio.

    :param request: Objeto da requisição HTTP.
    :type request: HttpRequest
    :returns: Página HTML do formulário ou redirecionamento para a listagem.
    :rtype: HttpResponse
    """
    if request.method == "POST":
        form = EventoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("gestao-eventos-list")
    else:
        form = EventoForm()
    return render(
        request,
        "core/eventos/form.html",
        {"form": form, "acao": "Criar"},
    )


@login_required
@require_http_methods(["GET"])
def gestao_evento_detalhe(
    request: HttpRequest, evento_id: uuid.UUID
) -> HttpResponse:
    """
    Exibe os detalhes de um evento específico na visão de gestão.

    :param request: Objeto da requisição HTTP.
    :type request: HttpRequest
    :param evento_id: UUID do evento a exibir.
    :type evento_id: uuid.UUID
    :returns: Página HTML com os detalhes do evento ou 404.
    :rtype: HttpResponse
    """
    evento = get_object_or_404(Evento, pk=evento_id)
    return render(request, "core/eventos/detalhe.html", {"evento": evento})


@login_required
@require_http_methods(["GET", "POST"])
def gestao_evento_editar(
    request: HttpRequest, evento_id: uuid.UUID
) -> HttpResponse:
    """
    Exibe o formulário de edição de evento e processa o envio.

    :param request: Objeto da requisição HTTP.
    :type request: HttpRequest
    :param evento_id: UUID do evento a editar.
    :type evento_id: uuid.UUID
    :returns: Página HTML do formulário preenchido ou redirecionamento.
    :rtype: HttpResponse
    """
    evento = get_object_or_404(Evento, pk=evento_id)
    if request.method == "POST":
        form = EventoForm(request.POST, request.FILES, instance=evento)
        if form.is_valid():
            form.save()
            return redirect("gestao-evento-detalhe", evento_id=evento.id)
    else:
        form = EventoForm(instance=evento)
    return render(
        request,
        "core/eventos/form.html",
        {"form": form, "acao": "Editar", "evento": evento},
    )


@login_required
@require_http_methods(["GET", "POST"])
def gestao_evento_deletar(
    request: HttpRequest, evento_id: uuid.UUID
) -> HttpResponse:
    """
    Exibe a página de confirmação de exclusão e processa a remoção.

    :param request: Objeto da requisição HTTP.
    :type request: HttpRequest
    :param evento_id: UUID do evento a remover.
    :type evento_id: uuid.UUID
    :returns: Página de confirmação ou redirecionamento para a listagem.
    :rtype: HttpResponse
    """
    evento = get_object_or_404(Evento, pk=evento_id)
    if request.method == "POST":
        evento.delete()
        return redirect("gestao-eventos-list")
    return render(
        request,
        "core/eventos/confirmar_deletar.html",
        {"evento": evento},
    )
