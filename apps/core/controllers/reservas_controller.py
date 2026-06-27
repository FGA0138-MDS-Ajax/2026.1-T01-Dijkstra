"""Controller HTTP para o dominio de Reservas de Espaço.

apps.core.controllers.reservas_controller
==========================================
Controller HTTP para o dominio de Reservas de Espaço.

Regras de negócio
-----------------
- Apenas **organizadores** (tipo="OR") podem solicitar e cancelar reservas.
- Apenas **gestores** (tipo="GE") podem aprovar ou reprovar reservas.
- A criação de uma reserva é bloqueada se já existir uma reserva APROVADA
  para o mesmo espaço com período sobreposto.
- A aprovação de uma reserva é bloqueada pelas mesmas condições.

Componentes Principais
----------------------
- :func:`reservas_do_evento`: lista as reservas de um evento com dados do evento.
- :func:`solicitar_reserva`: organizador solicita reserva para um evento.
- :func:`minhas_reservas`: organizador lista suas próprias reservas.
- :func:`cancelar_reserva`: organizador cancela uma reserva pendente.
- :func:`gestao_reservas_list`: gestor lista todas as reservas.
- :func:`gestao_reserva_detalhe`: gestor visualiza detalhes de uma reserva.
- :func:`aprovar_reserva`: gestor aprova uma reserva pendente.
- :func:`reprovar_reserva`: gestor reprova uma reserva pendente.

Notas
-----
- Requer Python >= 3.12
"""

from __future__ import annotations

import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from apps.core.forms import ReprovacaoReservaForm, ReservaEspacoForm
from apps.core.models.eventos_models import Evento
from apps.core.models.reservas_models import ReservaEspaco

__version__ = "0.0.1"
__license__ = "AGPL V3"


# ---------------------------------------------------------------------------
# Decoradores de permissão
# ---------------------------------------------------------------------------

def _somente_organizador(request: HttpRequest) -> None:
    """Lança PermissionDenied se o usuário não for organizador."""
    if not (request.user.is_authenticated and request.user.tipo == "OR"):
        raise PermissionDenied


def _somente_gestor(request: HttpRequest) -> None:
    """Lança PermissionDenied se o usuário não for gestor."""
    if not (request.user.is_authenticated and request.user.tipo == "GE"):
        raise PermissionDenied


# ---------------------------------------------------------------------------
# Lista de reservas de um evento
# ---------------------------------------------------------------------------

@login_required
@require_http_methods(["GET"])
def reservas_do_evento(request: HttpRequest, evento_id: uuid.UUID) -> HttpResponse:
    """
    Exibe as reservas de um evento específico junto com os dados do evento.

    Acessível a organizadores (para gerir suas reservas) e gestores
    (para acompanhar todas as reservas do evento).

    :param request: Objeto da requisição HTTP.
    :param evento_id: UUID do evento.
    :returns: Página HTML com dados do evento e lista de reservas.
    """
    if not request.user.is_authenticated or request.user.tipo not in ("OR", "GE"):
        raise PermissionDenied

    evento = get_object_or_404(Evento, pk=evento_id)
    reservas = (
        ReservaEspaco.objects.filter(evento=evento)
        .select_related("espaco", "solicitante", "avaliador")
        .order_by("-criado_em")
    )
    return render(
        request,
        "core/reservas/reservas_do_evento.html",
        {"evento": evento, "reservas": reservas},
    )


# ---------------------------------------------------------------------------
# Visões do Organizador
# ---------------------------------------------------------------------------

@login_required
@require_http_methods(["GET", "POST"])
def solicitar_reserva(request: HttpRequest, evento_id: uuid.UUID) -> HttpResponse:
    """
    Exibe o formulário de solicitação de reserva e processa o envio.

    Apenas organizadores (tipo="OR") podem acessar esta view.
    A criação é bloqueada se já houver uma reserva APROVADA conflitante.

    :param request: Objeto da requisição HTTP.
    :param evento_id: UUID do evento para o qual a reserva será solicitada.
    :returns: Formulário HTML ou redirecionamento.
    """
    _somente_organizador(request)
    evento = get_object_or_404(Evento, pk=evento_id)

    if request.method == "POST":
        form = ReservaEspacoForm(request.POST)
        if form.is_valid():
            espaco = form.cleaned_data["espaco"]
            data_inicio = form.cleaned_data["data_inicio"]
            data_fim = form.cleaned_data["data_fim"]

            if ReservaEspaco.tem_conflito(espaco, data_inicio, data_fim):
                messages.error(
                    request,
                    f"Já existe uma reserva aprovada para '{espaco.nome}' "
                    "neste período. Escolha outro horário ou espaço.",
                )
            else:
                reserva = form.save(commit=False)
                reserva.evento = evento
                reserva.solicitante = request.user
                reserva.status = ReservaEspaco.Status.PENDENTE
                reserva.save()
                messages.success(
                    request,
                    "Reserva solicitada com sucesso. Aguardando aprovação do gestor.",
                )
                return redirect("reservas-do-evento", evento_id=evento.id)
    else:
        form = ReservaEspacoForm()

    return render(
        request,
        "core/reservas/solicitar.html",
        {"form": form, "evento": evento},
    )


@login_required
@require_http_methods(["GET"])
def minhas_reservas(request: HttpRequest) -> HttpResponse:
    """
    Lista todas as reservas do organizador autenticado.

    :param request: Objeto da requisição HTTP.
    :returns: Página HTML com as reservas do organizador.
    """
    _somente_organizador(request)
    reservas = ReservaEspaco.objects.filter(
        solicitante=request.user
    ).select_related("espaco", "evento", "avaliador")
    return render(request, "core/reservas/minhas_reservas.html", {"reservas": reservas})


@login_required
@require_http_methods(["POST"])
def cancelar_reserva(request: HttpRequest, reserva_id: uuid.UUID) -> HttpResponse:
    """
    Cancela uma reserva PENDENTE do organizador autenticado.

    Apenas o próprio solicitante pode cancelar, e somente enquanto PENDENTE.

    :param request: Objeto da requisição HTTP.
    :param reserva_id: UUID da reserva a cancelar.
    :returns: Redirecionamento para a lista de reservas.
    """
    _somente_organizador(request)
    reserva = get_object_or_404(ReservaEspaco, pk=reserva_id, solicitante=request.user)

    evento_id = reserva.evento_id

    if reserva.status != ReservaEspaco.Status.PENDENTE:
        messages.error(
            request,
            "Apenas reservas pendentes podem ser canceladas.",
        )
    else:
        reserva.status = ReservaEspaco.Status.CANCELADA
        reserva.save(update_fields=["status"])
        messages.success(request, "Reserva cancelada com sucesso.")

    return redirect("reservas-do-evento", evento_id=evento_id)


# ---------------------------------------------------------------------------
# Visões do Gestor
# ---------------------------------------------------------------------------

@login_required
@require_http_methods(["GET"])
def gestao_reservas_list(request: HttpRequest) -> HttpResponse:
    """
    Lista todas as reservas do sistema para o gestor.

    Permite filtrar pelo status via query parameter ``?status=<valor>``.

    :param request: Objeto da requisição HTTP.
    :returns: Página HTML com a listagem de reservas.
    """
    _somente_gestor(request)
    status_filtro = request.GET.get("status", "")
    reservas = ReservaEspaco.objects.select_related(
        "espaco", "evento", "solicitante", "avaliador"
    )
    if status_filtro in ReservaEspaco.Status.values:
        reservas = reservas.filter(status=status_filtro)

    return render(
        request,
        "core/reservas/gestao_list.html",
        {
            "reservas": reservas,
            "status_choices": ReservaEspaco.Status.choices,
            "status_filtro": status_filtro,
        },
    )


@login_required
@require_http_methods(["GET"])
def gestao_reserva_detalhe(request: HttpRequest, reserva_id: uuid.UUID) -> HttpResponse:
    """
    Exibe os detalhes de uma reserva para o gestor.

    :param request: Objeto da requisição HTTP.
    :param reserva_id: UUID da reserva.
    :returns: Página HTML com os detalhes da reserva.
    """
    _somente_gestor(request)
    reserva = get_object_or_404(
        ReservaEspaco.objects.select_related("espaco", "evento", "solicitante"),
        pk=reserva_id,
    )
    form_reprovacao = ReprovacaoReservaForm()
    return render(
        request,
        "core/reservas/gestao_detalhe.html",
        {"reserva": reserva, "form_reprovacao": form_reprovacao},
    )


@login_required
@require_http_methods(["POST"])
def aprovar_reserva(request: HttpRequest, reserva_id: uuid.UUID) -> HttpResponse:
    """
    Aprova uma reserva PENDENTE.

    Bloqueia a aprovação se houver uma reserva APROVADA conflitante
    (mesmo espaço, período sobreposto).

    :param request: Objeto da requisição HTTP.
    :param reserva_id: UUID da reserva a aprovar.
    :returns: Redirecionamento para a listagem de gestão.
    """
    _somente_gestor(request)

    with transaction.atomic():
        # Bloqueia a própria reserva para evitar aprovações duplicadas concorrentes.
        reserva = get_object_or_404(
            ReservaEspaco.objects.select_for_update(), pk=reserva_id
        )

        if reserva.status != ReservaEspaco.Status.PENDENTE:
            messages.error(request, "Apenas reservas pendentes podem ser aprovadas.")
            return redirect("gestao-reservas-list")

        # Bloqueia todas as reservas do mesmo espaço com período sobreposto antes
        # de verificar conflito. Isso força serialização: se outra transação já
        # tiver aprovado uma reserva conflitante, este SELECT FOR UPDATE aguarda
        # o commit dela e enxerga o status atualizado na verificação seguinte.
        ReservaEspaco.objects.select_for_update().filter(
            espaco=reserva.espaco,
            data_inicio__lt=reserva.data_fim,
            data_fim__gt=reserva.data_inicio,
        ).exclude(pk=reserva.pk).count()

        if ReservaEspaco.tem_conflito(
            reserva.espaco, reserva.data_inicio, reserva.data_fim, excluir_pk=reserva.pk
        ):
            messages.error(
                request,
                f"Não é possível aprovar: já existe uma reserva aprovada para "
                f"'{reserva.espaco.nome}' neste período.",
            )
            return redirect("gestao-reserva-detalhe", reserva_id=reserva_id)

        reserva.status = ReservaEspaco.Status.APROVADA
        reserva.avaliador = request.user
        reserva.save(update_fields=["status", "avaliador"])

    messages.success(request, "Reserva aprovada com sucesso.")
    next_url = request.POST.get("next") or "gestao-reservas-list"
    if next_url.startswith("/"):
        return redirect(next_url)
    return redirect(next_url)


@login_required
@require_http_methods(["POST"])
def reprovar_reserva(request: HttpRequest, reserva_id: uuid.UUID) -> HttpResponse:
    """
    Reprova uma reserva PENDENTE, exigindo um motivo.

    :param request: Objeto da requisição HTTP.
    :param reserva_id: UUID da reserva a reprovar.
    :returns: Redirecionamento para a listagem de gestão ou volta ao detalhe.
    """
    _somente_gestor(request)
    reserva = get_object_or_404(ReservaEspaco, pk=reserva_id)

    if reserva.status != ReservaEspaco.Status.PENDENTE:
        messages.error(request, "Apenas reservas pendentes podem ser reprovadas.")
        return redirect("gestao-reservas-list")

    next_url = request.POST.get("next") or ""
    form = ReprovacaoReservaForm(request.POST, instance=reserva)
    if form.is_valid():
        reserva = form.save(commit=False)
        reserva.status = ReservaEspaco.Status.REPROVADA
        reserva.avaliador = request.user
        reserva.save(update_fields=["status", "avaliador", "motivo_reprovacao"])
        messages.success(request, "Reserva reprovada.")
        if next_url.startswith("/"):
            return redirect(next_url)
        return redirect("gestao-reservas-list")

    # Se o form for inválido (motivo vazio), retorna à origem com erro
    messages.error(request, "Informe o motivo da reprovação.")
    if next_url.startswith("/"):
        return redirect(next_url)
    return redirect("gestao-reserva-detalhe", reserva_id=reserva_id)
