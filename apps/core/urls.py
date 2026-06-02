"""
apps.core.urls
===============
Mapeamento de rotas URL para os domínios de Eventos e Espaços Físicos.

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

Notas
-----
- Requer Python >= 3.12
- Criado por `Gui-fga <https://github.com/Gui-fga>`_ em 30 maio 2026
- Revisado por `Saresu <https://github.com/Saresu>`_ em 30 maio 2026
"""

# compatibilidade
from __future__ import annotations

from django.urls import path
from apps.core.controllers.home_controller import home
from apps.core.controllers.eventos_controller import (
    EventosController,
    event_list_controller,
)
from apps.core.controllers.eventos_controller import detalhes_evento
from apps.core.controllers.espacos_controller import (
    espacos_list,
    espaco_novo,
    espaco_detalhe,
    espaco_editar,
    espaco_deletar,
)

__version__ = "0.0.1"
__license__ = "AGPL V3"


urlpatterns = [
    path("", home, name="home"),
    path("eventos/", EventosController.as_view(), name="eventos-list"),
    path("evento/<int:evento_id>/", detalhes_evento, name="detalhes_evento"),
    path("eventos-filtro/", event_list_controller, name="eventos-filtro"),
    # Espaços Físicos
    path("espacos/", espacos_list, name="espacos-list"),
    path("espacos/novo/", espaco_novo, name="espaco-novo"),
    path("espacos/<uuid:espaco_id>/", espaco_detalhe, name="espaco-detalhe"),
    path("espacos/<uuid:espaco_id>/editar/", espaco_editar, name="espaco-editar"),
    path("espacos/<uuid:espaco_id>/deletar/", espaco_deletar, name="espaco-deletar"),
]
