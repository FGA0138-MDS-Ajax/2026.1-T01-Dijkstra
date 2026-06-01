"""
apps.core.urls
===============
Mapeamento de rotas URL para o domínio de Eventos.

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

__version__ = "0.0.1"
__license__ = "AGPL V3"


urlpatterns = [
    path("", home, name="home"),
    path("eventos/", EventosController.as_view(), name="eventos-list"),
    path(
        "eventos/<int:evento_id>/", EventosController.as_view(), name="eventos-detail"
    ),
    path("eventos-filtro/", event_list_controller, name="eventos-filtro"),
]
