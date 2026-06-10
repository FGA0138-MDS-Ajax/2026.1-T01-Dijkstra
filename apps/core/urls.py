"""
apps.core.urls
===============
Mapeamento de rotas URL para os domínios de Eventos, Espaços Físicos e Organizações.

Componentes Principais
----------------------
- Rota raiz: renderiza a página inicial via
    :func:`~apps.core.controllers.home_controller.home`.
- Rota ``eventos/``: lista e criação de eventos via
    :class:`~apps.core.controllers.eventos_controller.EventosController`.
- Rota ``eventos/<int:evento_id>/``: detalhe, atualização e remoção de evento via
    :class:`~apps.core.controllers.eventos_controller.EventosController`.
- Rota ``eventos-filtro/``: filtragem de eventos por data via
    :func:`~apps.core.controllers.eventos_controller.event_list_controller`.
- Rota ``gestao/eventos/``: listagem de gestão via
    :func:`~apps.core.controllers.crud_eventos_controller.gestao_eventos_list`.
- Rota ``gestao/eventos/novo/``: formulário de criação via
    :func:`~apps.core.controllers.crud_eventos_controller.gestao_evento_novo`.
- Rota ``gestao/eventos/<uuid>/``: detalhe de gestão via
    :func:`~apps.core.controllers.crud_eventos_controller.gestao_evento_detalhe`.
- Rota ``gestao/eventos/<uuid>/editar/``: formulário de edição via
    :func:`~apps.core.controllers.crud_eventos_controller.gestao_evento_editar`.
- Rota ``gestao/eventos/<uuid>/deletar/``: confirmação e remoção via
    :func:`~apps.core.controllers.crud_eventos_controller.gestao_evento_deletar`.
- Rota ``espacos/``: listagem de espaços físicos em cards via
    :func:`~apps.core.controllers.espacos_controller.espacos_list`.
- Rota ``espacos/novo/``: formulário de criação via
    :func:`~apps.core.controllers.espacos_controller.espaco_novo`.
- Rota ``espacos/<uuid>/``: detalhe do espaço via
    :func:`~apps.core.controllers.espacos_controller.espaco_detalhe`.
- Rota ``espacos/<uuid>/editar/``: formulário de edição via
    :func:`~apps.core.controllers.espacos_controller.espaco_editar`.
- Rota ``espacos/<uuid>/deletar/``: confirmação e remoção via
    :func:`~apps.core.controllers.espacos_controller.espaco_deletar`.
- Rota ``organizacoes/``: listagem de organizações em cards via
    :func:`~apps.core.controllers.organizacoes_controller.organizacoes_list`.
- Rota ``organizacoes/nova/``: formulário de criação via
    :func:`~apps.core.controllers.organizacoes_controller.organizacao_nova`.
- Rota ``organizacoes/<uuid>/``: detalhe da organização via
    :func:`~apps.core.controllers.organizacoes_controller.organizacao_detalhe`.
- Rota ``organizacoes/<uuid>/editar/``: formulário de edição via
    :func:`~apps.core.controllers.organizacoes_controller.organizacao_editar`.
- Rota ``organizacoes/<uuid>/deletar/``: confirmação e remoção via
    :func:`~apps.core.controllers.organizacoes_controller.organizacao_deletar`.

Notas
-----
- Requer Python >= 3.12
- Criado por `Gui-fga <https://github.com/Gui-fga>`_ em 30 maio 2026
- Revisado por `Saresu <https://github.com/Saresu>`_ em 30 maio 2026
- Alterado por `MontMarcos <https://github.com/montmarcos>
    e `Beibeharry <https://github.com/beibeharry`_ em 02 junho 2026
- Alterado por `Welder60 <https://github.com/welder60>`_ em 02 junho 2026
- Lint por `Saresu <https://github.com/Saresu>`_ em 05 junho 2026
- Revisado por `Saresu <https://github.com/Saresu>`_ em 02 junho 2026
"""

# compatibilidade
from __future__ import annotations

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

# Importação do novo controlador de inscrições
from apps.core.controllers import inscricoes_controller
from apps.core.controllers import reservas_controller

__version__ = "0.0.4"
__license__ = "AGPL V3"

from django.core.exceptions import PermissionDenied

def somente_organizacao(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.tipo == "OR":
                return view_func(request, *args, **kwargs)
            raise PermissionDenied()
        return wrapper

urlpatterns = [
    path("", home, name="home"),
    path("eventos/", EventosController.as_view(), name="eventos-list"),
    path("evento/<uuid:evento_id>/", detalhes_evento, name="detalhes_evento"),
    path("eventos-filtro/", event_list_controller, name="eventos-filtro"),
    
    # Rota da US-007 (Inscrição)
    path("evento/<uuid:evento_id>/inscrever/", inscricoes_controller.inscrever_evento, name="inscrever_evento"),
    
    # Rota da US-009 (Cancelamento)
    path("evento/<uuid:evento_id>/cancelar/", inscricoes_controller.cancelar_inscricao, name="cancelar_inscricao"),

    # Reservas de Espaço — lista por evento e solicitação
    path(
        "evento/<uuid:evento_id>/reservas/",
        reservas_controller.reservas_do_evento,
        name="reservas-do-evento",
    ),
    path(
        "evento/<uuid:evento_id>/reservar/",
        reservas_controller.solicitar_reserva,
        name="solicitar-reserva",
    ),
    path(
        "reservas/minhas/",
        reservas_controller.minhas_reservas,
        name="minhas-reservas",
    ),
    path(
        "reservas/<uuid:reserva_id>/cancelar/",
        reservas_controller.cancelar_reserva,
        name="cancelar-reserva",
    ),

    # Reservas de Espaço — Gestor
    path(
        "gestao/reservas/",
        reservas_controller.gestao_reservas_list,
        name="gestao-reservas-list",
    ),
    path(
        "gestao/reservas/<uuid:reserva_id>/",
        reservas_controller.gestao_reserva_detalhe,
        name="gestao-reserva-detalhe",
    ),
    path(
        "gestao/reservas/<uuid:reserva_id>/aprovar/",
        reservas_controller.aprovar_reserva,
        name="aprovar-reserva",
    ),
    path(
        "gestao/reservas/<uuid:reserva_id>/reprovar/",
        reservas_controller.reprovar_reserva,
        name="reprovar-reserva",
    ),

    # Gestão de Eventos (CRUD)
    path("gestao/eventos/", somente_organizacao(gestao_eventos_list), name="gestao-eventos-list"),
    path("gestao/eventos/novo/", somente_organizacao(gestao_evento_novo), name="gestao-evento-novo"),
    path(
        "gestao/eventos/<uuid:evento_id>/",
        somente_organizacao(gestao_evento_detalhe),
        name="gestao-evento-detalhe",
    ),
    path(
        "gestao/eventos/<uuid:evento_id>/editar/",
        somente_organizacao(gestao_evento_editar),
        name="gestao-evento-editar",
    ),
    path(
        "gestao/eventos/<uuid:evento_id>/deletar/",
        somente_organizacao(gestao_evento_deletar),
        name="gestao-evento-deletar",
    ),
    # Espaços Físicos
    path("espacos/", somente_organizacao(espacos_list), name="espacos-list"),
    path("espacos/novo/", somente_organizacao(espaco_novo), name="espaco-novo"),
    path("espacos/<uuid:espaco_id>/", somente_organizacao(espaco_detalhe), name="espaco-detalhe"),
    path("espacos/<uuid:espaco_id>/editar/", somente_organizacao(espaco_editar), name="espaco-editar"),
    path("espacos/<uuid:espaco_id>/deletar/", somente_organizacao(espaco_deletar), name="espaco-deletar"),
    # Organizações Esportivas
    path("organizacoes/", somente_organizacao(organizacoes_list), name="organizacoes-list"),
    path("organizacoes/nova/", somente_organizacao(organizacao_nova), name="organizacao-nova"),
    path(
        "organizacoes/<uuid:organizacao_id>/",
        somente_organizacao(organizacao_detalhe),
        name="organizacao-detalhe",
    ),
    path(
        "organizacoes/<uuid:organizacao_id>/editar/",
        somente_organizacao(organizacao_editar),
        name="organizacao-editar",
    ),
    path(
        "organizacoes/<uuid:organizacao_id>/deletar/",
        somente_organizacao(organizacao_deletar),
        name="organizacao-deletar",
    ),
]