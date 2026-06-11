"""
apps.core.urls
===============
Mapeamento de rotas URL para os dominios de Eventos, Espacos Fisicos,
Organizacoes e Membros de Organizacoes.

Notas
-----
- Requer Python >= 3.12
- Criado por Gui-fga em 30 maio 2026
- Revisado por Saresu em 30 maio 2026
- Alterado por MontMarcos e Beibeharry em 02 junho 2026
- Alterado por Welder60 em 02 junho 2026
- Lint por Saresu em 05 junho 2026
"""

from __future__ import annotations

from django.core.exceptions import PermissionDenied
from django.urls import path

from apps.core.controllers.home_controller import home
from apps.core.controllers.eventos_controller import (
    EventosController,
    event_list_controller,
    detalhes_evento,
)
from apps.core.controllers.crud_eventos_controller import (
    gestao_eventos_list,
    gestao_evento_novo,
    gestao_evento_detalhe,
    gestao_evento_editar,
    gestao_evento_deletar,
)
from apps.core.controllers.espacos_controller import (
    espacos_list,
    espaco_novo,
    espaco_detalhe,
    espaco_editar,
    espaco_deletar,
)
from apps.core.controllers.organizacoes_controller import (
    organizacoes_list,
    organizacao_nova,
    organizacao_detalhe,
    organizacao_editar,
    organizacao_deletar,
)
from apps.core.controllers.membros_organizacao_controller import (
    membros_list,
    adicionar_membro,
    remover_membro,
)
from apps.core.controllers import inscricoes_controller
from apps.core.controllers import reservas_controller

__version__ = "0.0.6"
__license__ = "AGPL V3"


def somente_organizacao(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.tipo == "OR":
            return view_func(request, *args, **kwargs)
        raise PermissionDenied()
    return wrapper


def somente_gestor(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.tipo == "GE":
            return view_func(request, *args, **kwargs)
        raise PermissionDenied()
    return wrapper


def gestor_ou_organizacao(view_func):
    """Permite acesso a gestores (GE) e organizadores (OR)."""
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.tipo in ("GE", "OR"):
            return view_func(request, *args, **kwargs)
        raise PermissionDenied()
    return wrapper


urlpatterns = [
    path("", home, name="home"),
    path("eventos/", EventosController.as_view(), name="eventos-list"),
    path("evento/<uuid:evento_id>/", detalhes_evento, name="detalhes_evento"),
    path("eventos-filtro/", event_list_controller, name="eventos-filtro"),

    # US-007 Inscricao
    path("evento/<uuid:evento_id>/inscrever/", inscricoes_controller.inscrever_evento, name="inscrever_evento"),

    # US-009 Cancelamento
    path("evento/<uuid:evento_id>/cancelar/", inscricoes_controller.cancelar_inscricao, name="cancelar_inscricao"),

    # Reservas de Espaco
    path("evento/<uuid:evento_id>/reservas/", reservas_controller.reservas_do_evento, name="reservas-do-evento"),
    path("evento/<uuid:evento_id>/reservar/", reservas_controller.solicitar_reserva, name="solicitar-reserva"),
    path("reservas/minhas/", reservas_controller.minhas_reservas, name="minhas-reservas"),
    path("reservas/<uuid:reserva_id>/cancelar/", reservas_controller.cancelar_reserva, name="cancelar-reserva"),

    # Reservas - Gestor
    path("gestao/reservas/", reservas_controller.gestao_reservas_list, name="gestao-reservas-list"),
    path("gestao/reservas/<uuid:reserva_id>/", reservas_controller.gestao_reserva_detalhe, name="gestao-reserva-detalhe"),
    path("gestao/reservas/<uuid:reserva_id>/aprovar/", reservas_controller.aprovar_reserva, name="aprovar-reserva"),
    path("gestao/reservas/<uuid:reserva_id>/reprovar/", reservas_controller.reprovar_reserva, name="reprovar-reserva"),

    # Gestao de Eventos (CRUD)
    path("gestao/eventos/", somente_organizacao(gestao_eventos_list), name="gestao-eventos-list"),
    path("gestao/eventos/novo/", somente_organizacao(gestao_evento_novo), name="gestao-evento-novo"),
    path("gestao/eventos/<uuid:evento_id>/", somente_organizacao(gestao_evento_detalhe), name="gestao-evento-detalhe"),
    path("gestao/eventos/<uuid:evento_id>/editar/", somente_organizacao(gestao_evento_editar), name="gestao-evento-editar"),
    path("gestao/eventos/<uuid:evento_id>/deletar/", somente_organizacao(gestao_evento_deletar), name="gestao-evento-deletar"),

    # Espacos Fisicos
    path("espacos/", somente_gestor(espacos_list), name="espacos-list"),
    path("espacos/novo/", somente_gestor(espaco_novo), name="espaco-novo"),
    path("espacos/<uuid:espaco_id>/", somente_gestor(espaco_detalhe), name="espaco-detalhe"),
    path("espacos/<uuid:espaco_id>/editar/", somente_gestor(espaco_editar), name="espaco-editar"),
    path("espacos/<uuid:espaco_id>/deletar/", somente_gestor(espaco_deletar), name="espaco-deletar"),

    # Organizacoes Esportivas (gestor e organizador)
    path("organizacoes/", gestor_ou_organizacao(organizacoes_list), name="organizacoes-list"),
    path("organizacoes/nova/", gestor_ou_organizacao(organizacao_nova), name="organizacao-nova"),
    path("organizacoes/<uuid:organizacao_id>/", gestor_ou_organizacao(organizacao_detalhe), name="organizacao-detalhe"),
    path("organizacoes/<uuid:organizacao_id>/editar/", gestor_ou_organizacao(organizacao_editar), name="organizacao-editar"),
    path("organizacoes/<uuid:organizacao_id>/deletar/", gestor_ou_organizacao(organizacao_deletar), name="organizacao-deletar"),

    # Membros da Organizacao (somente Gestor)
    path("organizacoes/<uuid:organizacao_id>/membros/", somente_gestor(membros_list), name="organizacao-membros"),
    path("organizacoes/<uuid:organizacao_id>/membros/adicionar/", somente_gestor(adicionar_membro), name="organizacao-adicionar-membro"),
    path("organizacoes/<uuid:organizacao_id>/membros/<uuid:usuario_id>/remover/", somente_gestor(remover_membro), name="organizacao-remover-membro"),
]
