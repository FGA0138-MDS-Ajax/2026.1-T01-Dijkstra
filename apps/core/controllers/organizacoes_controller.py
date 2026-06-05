"""
apps.core.controllers.organizacoes_controller
===============================================
Controller HTTP para o domínio de Organizações Esportivas Universitárias.

Componentes Principais
----------------------
- :func:`organizacoes_list`: exibe a listagem de organizações em cards.
- :func:`organizacao_nova`: exibe e processa o formulário de criação.
- :func:`organizacao_detalhe`: exibe os detalhes de uma organização.
- :func:`organizacao_editar`: exibe e processa o formulário de edição.
- :func:`organizacao_deletar`: exibe confirmação e processa a remoção.

Notas
-----
- Requer Python >= 3.12
- Criado por `Welder60 <https://github.com/welder60>`_ em 02 junho 2026
"""

# compatibilidade
from __future__ import annotations

import uuid

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods

from apps.core.models.organizacoes_models import Organizacao
from apps.core.services.organizacoes_service import OrganizacoesService
from apps.core.forms import OrganizacaoForm

__version__ = "0.0.1"
__license__ = "AGPL V3"

_service = OrganizacoesService()


@login_required
@require_http_methods(["GET"])
def organizacoes_list(request: HttpRequest) -> HttpResponse:
    """
    Exibe a listagem de todas as organizações em cards.

    :param request: Objeto da requisição HTTP.
    :type request: HttpRequest
    :returns: Página HTML com os cards de organizações.
    :rtype: HttpResponse
    """
    organizacoes = _service.listar_organizacoes()
    return render(
        request,
        "core/organizacoes/list.html",
        {"organizacoes": organizacoes},
    )


@login_required
@require_http_methods(["GET", "POST"])
def organizacao_nova(request: HttpRequest) -> HttpResponse:
    """
    Exibe o formulário de criação de organização e processa o envio.

    :param request: Objeto da requisição HTTP.
    :type request: HttpRequest
    :returns: Página HTML do formulário ou redirecionamento para a listagem.
    :rtype: HttpResponse
    """
    if request.method == "POST":
        form = OrganizacaoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("organizacoes-list")
    else:
        form = OrganizacaoForm()
    return render(
        request,
        "core/organizacoes/form.html",
        {"form": form, "acao": "Criar"},
    )


@login_required
@require_http_methods(["GET"])
def organizacao_detalhe(request: HttpRequest, organizacao_id: uuid.UUID) -> HttpResponse:
    """
    Exibe os detalhes de uma organização específica.

    :param request: Objeto da requisição HTTP.
    :type request: HttpRequest
    :param organizacao_id: UUID da organização a exibir.
    :type organizacao_id: uuid.UUID
    :returns: Página HTML com os detalhes da organização ou 404.
    :rtype: HttpResponse
    """
    organizacao = get_object_or_404(Organizacao, pk=organizacao_id)
    return render(
        request,
        "core/organizacoes/detalhe.html",
        {"organizacao": organizacao},
    )


@login_required
@require_http_methods(["GET", "POST"])
def organizacao_editar(
    request: HttpRequest, organizacao_id: uuid.UUID
) -> HttpResponse:
    """
    Exibe o formulário de edição de organização e processa o envio.

    :param request: Objeto da requisição HTTP.
    :type request: HttpRequest
    :param organizacao_id: UUID da organização a editar.
    :type organizacao_id: uuid.UUID
    :returns: Página HTML do formulário preenchido ou redirecionamento.
    :rtype: HttpResponse
    """
    organizacao = get_object_or_404(Organizacao, pk=organizacao_id)
    if request.method == "POST":
        form = OrganizacaoForm(request.POST, request.FILES, instance=organizacao)
        if form.is_valid():
            form.save()
            return redirect("organizacao-detalhe", organizacao_id=organizacao.id)
    else:
        form = OrganizacaoForm(instance=organizacao)
    return render(
        request,
        "core/organizacoes/form.html",
        {"form": form, "acao": "Editar", "organizacao": organizacao},
    )


@login_required
@require_http_methods(["GET", "POST"])
def organizacao_deletar(
    request: HttpRequest, organizacao_id: uuid.UUID
) -> HttpResponse:
    """
    Exibe a página de confirmação de exclusão e processa a remoção.

    :param request: Objeto da requisição HTTP.
    :type request: HttpRequest
    :param organizacao_id: UUID da organização a remover.
    :type organizacao_id: uuid.UUID
    :returns: Página de confirmação ou redirecionamento para a listagem.
    :rtype: HttpResponse
    """
    organizacao = get_object_or_404(Organizacao, pk=organizacao_id)
    if request.method == "POST":
        organizacao.delete()
        return redirect("organizacoes-list")
    return render(
        request,
        "core/organizacoes/confirmar_deletar.html",
        {"organizacao": organizacao},
    )
