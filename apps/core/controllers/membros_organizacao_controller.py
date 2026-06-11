"""
apps.core.controllers.membros_organizacao_controller
=====================================================
Controller HTTP para gestão de membros de Organizações Esportivas.

Componentes Principais
----------------------
- :func:`membros_list`: exibe a lista de membros e o formulário de adição.
- :func:`adicionar_membro`: processa a adição de um novo membro.
- :func:`remover_membro`: processa a remoção de um membro.

Notas
-----
- Requer Python >= 3.12
- Acesso restrito a usuários com perfil Gestor.
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

__version__ = "0.0.1"
__license__ = "AGPL V3"

_service = OrganizacoesService()


@login_required
@require_http_methods(["GET"])
def membros_list(request: HttpRequest, organizacao_id: uuid.UUID) -> HttpResponse:
    """
    Exibe a lista de membros de uma organização e os usuários disponíveis
    para adição.

    :param request: Objeto da requisição HTTP.
    :param organizacao_id: UUID da organização.
    :returns: Página HTML de gestão de membros.
    :rtype: HttpResponse
    """
    organizacao = get_object_or_404(Organizacao, pk=organizacao_id)
    membros = _service.listar_membros(organizacao_id)
    disponiveis = _service.listar_usuarios_sem_vinculo(organizacao_id)
    return render(
        request,
        "core/organizacoes/membros.html",
        {
            "organizacao": organizacao,
            "membros": membros,
            "disponiveis": disponiveis,
        },
    )


@login_required
@require_http_methods(["POST"])
def adicionar_membro(request: HttpRequest, organizacao_id: uuid.UUID) -> HttpResponse:
    """
    Processa a adição de um usuário como membro da organização.

    :param request: Objeto da requisição HTTP (POST com ``usuario_id``).
    :param organizacao_id: UUID da organização.
    :returns: Redirecionamento para a página de membros.
    :rtype: HttpResponse
    """
    usuario_id = request.POST.get("usuario_id")
    if usuario_id:
        _service.adicionar_membro(organizacao_id, uuid.UUID(usuario_id))
    return redirect("organizacao-membros", organizacao_id=organizacao_id)


@login_required
@require_http_methods(["POST"])
def remover_membro(
    request: HttpRequest, organizacao_id: uuid.UUID, usuario_id: uuid.UUID
) -> HttpResponse:
    """
    Processa a remoção de um membro da organização.

    :param request: Objeto da requisição HTTP.
    :param organizacao_id: UUID da organização.
    :param usuario_id: UUID do usuário a remover.
    :returns: Redirecionamento para a página de membros.
    :rtype: HttpResponse
    """
    _service.remover_membro(organizacao_id, usuario_id)
    return redirect("organizacao-membros", organizacao_id=organizacao_id)
