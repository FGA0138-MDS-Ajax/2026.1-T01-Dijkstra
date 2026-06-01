"""
apps.core.controllers.home_controller
=======================================
Controller HTTP para a página inicial do domínio de Eventos.

Componentes Principais
----------------------
- :func:`home`: view Django que renderiza a página inicial com a listagem de eventos.

Notas
-----
- Requer Python >= 3.12
- Criado por `Gui-fga <https://github.com/Gui-fga>`_ em 30 maio 2026
- Revisado por `Saresu <https://github.com/Saresu>`_ em 30 maio 2026
"""

# compatibilidade
from __future__ import annotations

from django.shortcuts import render
from django.core.paginator import Paginator
from apps.core.services.eventos_service import EventosService

__version__ = "0.0.1"
__license__ = "AGPL V3"


def home(request):
    """
    Renderiza a página inicial com a listagem de todos os eventos e filtros.
    """

    service = EventosService()

    # Captura filtros da requisição
    query = request.GET.get("q")
    data_inicio = request.GET.get("data_inicio")
    data_fim = request.GET.get("data_fim")

    # Busca eventos filtrados via Service
    eventos_list = service.get_filtered_events(
        query=query,
        data_inicio=data_inicio,
        data_fim=data_fim
    )

    # Paginação: 6 eventos por página
    paginator = Paginator(eventos_list, 6)
    page_number = request.GET.get("page")
    eventos_obj = paginator.get_page(page_number)

    return render(request, "core/index.html", {"eventos": eventos_obj})
