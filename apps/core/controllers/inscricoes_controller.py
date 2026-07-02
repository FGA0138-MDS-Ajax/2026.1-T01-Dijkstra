"""Controller HTTP para o dominio de Inscrições.

apps.core.controllers.inscricoes_controller
===========================================
Controller HTTP para o dominio de Inscrições.

Componentes Principais
----------------------
- :func:`inscrever_evento`: Registra a inscrição de um aluno em um evento.
- :func:`cancelar_inscricao`: Cancela a inscrição de um aluno.
- :func:`gestao_inscricoes`: Lista inscritos de um evento (organizador).
- :func:`aprovar_inscricao`: Aprova uma inscrição pendente.
- :func:`reprovar_inscricao`: Reprova uma inscrição com justificativa.
- :func:`aprovar_todas_pendentes`: Aprova em lote todas as inscrições pendentes.
- :func:`exportar_inscricoes_csv`: Exporta a lista de inscritos como CSV.

Notas
-----
- Requer Python >= 3.12
- Criado por `DaviiGualbertoo <https://github.com/DaviiGualbertoo>`_ em 08 junho 2026
- Lint por Saresu 02 julho 2026
"""

from __future__ import annotations

import csv
import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from apps.core.forms import ReprovacaoInscricaoForm
from apps.core.models.eventos_models import Evento
from apps.core.models.inscricao_models import Inscricao

__version__ = "0.0.3"
__license__ = "AGPL V3"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _somente_organizador(request: HttpRequest) -> None:
    """Lança PermissionDenied se o usuário não for organizador."""
    if not (request.user.is_authenticated and request.user.tipo == "OR"):
        raise PermissionDenied


# ---------------------------------------------------------------------------
# Visões do Aluno
# ---------------------------------------------------------------------------


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
        ja_inscrito = Inscricao.objects.filter(
            aluno=request.user, evento=evento
        ).exists()

        if ja_inscrito:
            messages.warning(request, "Você já está inscrito neste evento.")
        else:
            vagas_ocupadas = (
                Inscricao.objects.filter(evento=evento)
                .exclude(
                    status__in=[Inscricao.Status.CANCELADA, Inscricao.Status.REJEITADA]
                )
                .count()
            )

            vagas_disponiveis = evento.capacidade - vagas_ocupadas

            if vagas_disponiveis > 0:
                Inscricao.objects.create(aluno=request.user, evento=evento)
                messages.success(request, "Inscrição solicitada. Aguardando aprovação.")
            else:
                messages.error(
                    request, "Não há mais vagas disponíveis para este evento."
                )

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
            inscricao.delete()
            messages.success(request, "Inscrição cancelada com sucesso.")

    return redirect(request.META.get("HTTP_REFERER", "home"))


# ---------------------------------------------------------------------------
# Visões do Organizador — gestão de inscritos
# ---------------------------------------------------------------------------


@login_required
@require_http_methods(["GET"])
def gestao_inscricoes(request: HttpRequest, evento_id: uuid.UUID) -> HttpResponse:
    """
    Lista os inscritos de um evento de forma paginada, com filtro por status.

    Exibe também um resumo dos dados do evento no topo da página.

    :param request: Objeto da requisição HTTP.
    :param evento_id: UUID do evento.
    :returns: Página HTML com a listagem de inscritos.
    """
    _somente_organizador(request)
    evento = get_object_or_404(Evento, pk=evento_id)

    status_filtro = request.GET.get("status", "")
    inscricoes_qs = (
        Inscricao.objects.filter(evento=evento)
        .select_related("aluno", "avaliador")
        .order_by("-data_solicitacao")
    )
    if status_filtro in Inscricao.Status.values:
        inscricoes_qs = inscricoes_qs.filter(status=status_filtro)

    paginator = Paginator(inscricoes_qs, 15)
    page_obj = paginator.get_page(request.GET.get("page"))

    # Contagens para o resumo
    total = Inscricao.objects.filter(evento=evento).count()
    pendentes = Inscricao.objects.filter(
        evento=evento, status=Inscricao.Status.PENDENTE
    ).count()
    aprovadas = Inscricao.objects.filter(
        evento=evento, status=Inscricao.Status.APROVADA
    ).count()
    rejeitadas = Inscricao.objects.filter(
        evento=evento, status=Inscricao.Status.REJEITADA
    ).count()

    form_reprovacao = ReprovacaoInscricaoForm()

    return render(
        request,
        "core/inscricoes/gestao_inscricoes.html",
        {
            "evento": evento,
            "page_obj": page_obj,
            "status_choices": Inscricao.Status.choices,
            "status_filtro": status_filtro,
            "form_reprovacao": form_reprovacao,
            "total": total,
            "pendentes": pendentes,
            "aprovadas": aprovadas,
            "rejeitadas": rejeitadas,
        },
    )


@login_required
@require_http_methods(["POST"])
def aprovar_inscricao(request: HttpRequest, inscricao_id: uuid.UUID) -> HttpResponse:
    """
    Aprova uma inscrição PENDENTE.

    :param request: Objeto da requisição HTTP.
    :param inscricao_id: UUID da inscrição a aprovar.
    :returns: Redirecionamento para a gestão de inscritos do evento.
    """
    _somente_organizador(request)
    inscricao = get_object_or_404(
        Inscricao.objects.select_related("evento"), pk=inscricao_id
    )

    if inscricao.status != Inscricao.Status.PENDENTE:
        messages.error(request, "Apenas inscrições pendentes podem ser aprovadas.")
    else:
        inscricao.status = Inscricao.Status.APROVADA
        inscricao.avaliador = request.user
        inscricao.data_avaliacao = timezone.now()
        inscricao.save(update_fields=["status", "avaliador", "data_avaliacao"])
        messages.success(
            request,
            f"Inscrição de {inscricao.aluno.get_full_name() or inscricao.aluno.username} aprovada.",
        )

    return redirect("gestao-inscricoes", evento_id=inscricao.evento_id)


@login_required
@require_http_methods(["POST"])
def reprovar_inscricao(request: HttpRequest, inscricao_id: uuid.UUID) -> HttpResponse:
    """
    Reprova uma inscrição PENDENTE, exigindo motivo obrigatório.

    :param request: Objeto da requisição HTTP.
    :param inscricao_id: UUID da inscrição a reprovar.
    :returns: Redirecionamento para a gestão de inscritos do evento.
    """
    _somente_organizador(request)
    inscricao = get_object_or_404(
        Inscricao.objects.select_related("evento"), pk=inscricao_id
    )

    if inscricao.status != Inscricao.Status.PENDENTE:
        messages.error(request, "Apenas inscrições pendentes podem ser reprovadas.")
        return redirect("gestao-inscricoes", evento_id=inscricao.evento_id)

    form = ReprovacaoInscricaoForm(request.POST, instance=inscricao)
    if form.is_valid():
        inscricao = form.save(commit=False)
        inscricao.status = Inscricao.Status.REJEITADA
        inscricao.avaliador = request.user
        inscricao.data_avaliacao = timezone.now()
        inscricao.save(
            update_fields=["status", "avaliador", "data_avaliacao", "motivo_reprovacao"]
        )
        messages.success(
            request,
            f"Inscrição de {inscricao.aluno.get_full_name() or inscricao.aluno.username} "
            " reprovada.",
        )
    else:
        messages.error(request, "Informe o motivo da reprovação.")

    return redirect("gestao-inscricoes", evento_id=inscricao.evento_id)


@login_required
@require_http_methods(["POST"])
def aprovar_todas_pendentes(request: HttpRequest, evento_id: uuid.UUID) -> HttpResponse:
    """
    Aprova em lote todas as inscrições PENDENTES de um evento.

    :param request: Objeto da requisição HTTP.
    :param evento_id: UUID do evento.
    :returns: Redirecionamento para a gestão de inscritos.
    """
    _somente_organizador(request)
    evento = get_object_or_404(Evento, pk=evento_id)

    pendentes_qs = Inscricao.objects.filter(
        evento=evento, status=Inscricao.Status.PENDENTE
    )
    count = pendentes_qs.count()

    if count == 0:
        messages.warning(request, "Não há inscrições pendentes para aprovar.")
    else:
        pendentes_qs.update(
            status=Inscricao.Status.APROVADA,
            avaliador=request.user,
            data_avaliacao=timezone.now(),
        )
        messages.success(request, f"{count} inscrição(ões) aprovada(s) com sucesso.")

    return redirect("gestao-inscricoes", evento_id=evento_id)


@login_required
@require_http_methods(["GET"])
def exportar_inscricoes_csv(request: HttpRequest, evento_id: uuid.UUID) -> HttpResponse:
    """
    Exporta a lista de inscritos de um evento no formato CSV.

    :param request: Objeto da requisição HTTP.
    :param evento_id: UUID do evento.
    :returns: Resposta HTTP com o arquivo CSV.
    """
    _somente_organizador(request)
    evento = get_object_or_404(Evento, pk=evento_id)

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = (
        f'attachment; filename="inscritos_{evento.nome[:40].replace(" ", "_")}.csv"'
    )
    response.write("﻿")  # BOM para compatibilidade com Excel

    writer = csv.writer(response, delimiter=";")
    writer.writerow(
        [
            "Nome",
            "E-mail",
            "Status",
            "Data da Solicitação",
            "Avaliador",
            "Data da Avaliação",
            "Motivo da Reprovação",
        ]
    )

    inscricoes = (
        Inscricao.objects.filter(evento=evento)
        .select_related("aluno", "avaliador")
        .order_by("aluno__first_name", "aluno__last_name")
    )

    for inscricao in inscricoes:
        avaliador_nome = ""
        if inscricao.avaliador:
            avaliador_nome = (
                inscricao.avaliador.get_full_name() or inscricao.avaliador.username
            )

        writer.writerow(
            [
                inscricao.aluno.get_full_name() or inscricao.aluno.username,
                inscricao.aluno.email,
                inscricao.get_status_display(),
                inscricao.data_solicitacao.strftime("%d/%m/%Y %H:%M")
                if inscricao.data_solicitacao
                else "",
                avaliador_nome,
                inscricao.data_avaliacao.strftime("%d/%m/%Y %H:%M")
                if inscricao.data_avaliacao
                else "",
                inscricao.motivo_reprovacao or "",
            ]
        )

    return response
