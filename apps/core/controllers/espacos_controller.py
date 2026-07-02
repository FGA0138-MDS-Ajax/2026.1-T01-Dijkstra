"""
apps.core.controllers.espacos_controller
==========================================
Controller HTTP para o domínio de Espaços Físicos.

Componentes Principais
----------------------
- :func:`espacos_list`: exibe a listagem de espaços em cards.
- :func:`espaco_novo`: exibe e processa o formulário de criação.
- :func:`espaco_detalhe`: exibe os detalhes de um espaço.
- :func:`espaco_editar`: exibe e processa o formulário de edição.
- :func:`espaco_deletar`: processa a remoção (confirmação em modal no front).

Notas
-----
- Requer Python >= 3.12
- Criado por `Welder60 <https://github.com/welder60>`_ em 01 de junho de 2026
"""

# compatibilidade
from __future__ import annotations

import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods

from apps.core.models.espacos_models import EspacoFisico
from apps.core.services.espacos_service import EspacosService
from apps.core.forms import EspacoFisicoForm

__version__ = "0.0.1"
__license__ = "AGPL V3"

_service = EspacosService()


@login_required
@require_http_methods(["GET"])
def espacos_list(request: HttpRequest) -> HttpResponse:
    """
    Exibe a listagem de todos os espaços físicos em cards.

    :param request: Objeto da requisição HTTP.
    :type request: HttpRequest
    :returns: Página HTML com os cards de espaços.
    :rtype: HttpResponse
    """
    espacos = _service.listar_espacos()
    return render(request, "core/espacos/list.html", {"espacos": espacos})


@login_required
@require_http_methods(["GET", "POST"])
def espaco_novo(request: HttpRequest) -> HttpResponse:
    """
    Exibe o formulário de criação de espaço e processa o envio.

    :param request: Objeto da requisição HTTP.
    :type request: HttpRequest
    :returns: Página HTML do formulário ou redirecionamento para a listagem.
    :rtype: HttpResponse
    """
    if request.method == "POST":
        form = EspacoFisicoForm(request.POST, request.FILES)
        if form.is_valid():
            espaco = form.save()
            messages.success(request, f'Espaço "{espaco.nome}" criado com sucesso.')
            return redirect("espacos-list")
        messages.error(request, "Não foi possível criar o espaço. Verifique os campos destacados.")
    else:
        form = EspacoFisicoForm()
    return render(request, "core/espacos/form.html", {"form": form, "acao": "Criar"})


@login_required
@require_http_methods(["GET"])
def espaco_detalhe(request: HttpRequest, espaco_id: uuid.UUID) -> HttpResponse:
    """
    Exibe os detalhes de um espaço físico específico.

    :param request: Objeto da requisição HTTP.
    :type request: HttpRequest
    :param espaco_id: UUID do espaço a exibir.
    :type espaco_id: uuid.UUID
    :returns: Página HTML com os detalhes do espaço ou 404.
    :rtype: HttpResponse
    """
    espaco = get_object_or_404(EspacoFisico, pk=espaco_id)
    return render(request, "core/espacos/detalhe.html", {"espaco": espaco})


@login_required
@require_http_methods(["GET", "POST"])
def espaco_editar(request: HttpRequest, espaco_id: uuid.UUID) -> HttpResponse:
    """
    Exibe o formulário de edição de espaço e processa o envio.

    :param request: Objeto da requisição HTTP.
    :type request: HttpRequest
    :param espaco_id: UUID do espaço a editar.
    :type espaco_id: uuid.UUID
    :returns: Página HTML do formulário preenchido ou redirecionamento.
    :rtype: HttpResponse
    """
    espaco = get_object_or_404(EspacoFisico, pk=espaco_id)
    if request.method == "POST":
        form = EspacoFisicoForm(request.POST, request.FILES, instance=espaco)
        if form.is_valid():
            form.save()
            messages.success(request, f'Espaço "{espaco.nome}" atualizado com sucesso.')
            return redirect("espaco-detalhe", espaco_id=espaco.id)
        messages.error(request, "Não foi possível salvar as alterações. Verifique os campos destacados.")
    else:
        form = EspacoFisicoForm(instance=espaco)
    return render(
        request,
        "core/espacos/form.html",
        {"form": form, "acao": "Editar", "espaco": espaco},
    )


@login_required
@require_http_methods(["POST"])
def espaco_deletar(request: HttpRequest, espaco_id: uuid.UUID) -> HttpResponse:
    """
    Processa a remoção de um espaço (a confirmação ocorre em modal no front).

    :param request: Objeto da requisição HTTP.
    :type request: HttpRequest
    :param espaco_id: UUID do espaço a remover.
    :type espaco_id: uuid.UUID
    :returns: Redirecionamento para a listagem.
    :rtype: HttpResponse
    """
    espaco = get_object_or_404(EspacoFisico, pk=espaco_id)
    nome = espaco.nome
    espaco.delete()
    messages.success(request, f'Espaço "{nome}" excluído com sucesso.')
    return redirect("espacos-list")
