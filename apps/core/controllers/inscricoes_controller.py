"""Controller HTTP para o dominio de Inscrições.

apps.core.controllers.inscricoes_controller
apps.core.controllers.inscricoes_controller
===========================================
Controller HTTP para o dominio de Inscrições.

Componentes Principais
----------------------
- :func:`inscrever_evento`: Registra a inscrição de um aluno em um evento.
- :func:`cancelar_inscricao`: Cancela a inscrição de um aluno.

Notas
-----
- Requer Python >= 3.12
- Criado por `DaviiGualbertoo <https://github.com/DaviiGualbertoo>`_ em 08 junho 2026
"""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect

from apps.core.models.eventos_models import Evento
from apps.core.models.inscricao_models import Inscricao

__version__ = "0.0.1"
__license__ = "AGPL V3"


@login_required
def inscrever_evento(request: HttpRequest, evento_id: str) -> HttpResponse:
    """
    Registra a inscrição de um aluno em um evento.

    :param request: Objeto da requisição HTTP.
    :type request: HttpRequest
    :param evento_id: UUID do evento alvo.
    :type evento_id: str
    :returns: Redirecionamento para a página de origem.
    :rtype: HttpResponse
    """
    if request.method == "POST":
        evento = get_object_or_404(Evento, id=evento_id)
        ja_inscrito = Inscricao.objects.filter(aluno=request.user, evento=evento).exists()

        if ja_inscrito:
            messages.warning(request, "Você já está inscrito neste evento.")
        else:
            # Cálculo dinâmico das vagas: Capacidade - Inscrições Ativas (ignorando rejeitadas/canceladas)
            vagas_ocupadas = Inscricao.objects.filter(
                evento=evento
            ).exclude(
                status__in=[Inscricao.Status.CANCELADA, Inscricao.Status.REJEITADA]
            ).count()
            
            vagas_disponiveis = evento.capacidade - vagas_ocupadas

            if vagas_disponiveis > 0:
                Inscricao.objects.create(aluno=request.user, evento=evento)
                messages.success(request, "Inscrição solicitada. Aguardando aprovação.")
            else:
                messages.error(request, "Não há mais vagas disponíveis para este evento.")
                
    return redirect(request.META.get("HTTP_REFERER", "home"))


@login_required
def cancelar_inscricao(request: HttpRequest, evento_id: str) -> HttpResponse:
    """
    Cancela a inscrição de um aluno em um evento e libera a vaga.

    :param request: Objeto da requisição HTTP.
    :type request: HttpRequest
    :param evento_id: UUID do evento alvo.
    :type evento_id: str
    :returns: Redirecionamento para a página de origem.
    :rtype: HttpResponse
    """
    if request.method == "POST":
        evento = get_object_or_404(Evento, id=evento_id)
        inscricao = Inscricao.objects.filter(aluno=request.user, evento=evento).first()

        if inscricao:
            # Como usamos cálculo dinâmico, apagar a inscrição já libera a vaga automaticamente
            inscricao.delete()
            messages.success(request, "Inscrição cancelada com sucesso.")
            
    return redirect(request.META.get("HTTP_REFERER", "home"))