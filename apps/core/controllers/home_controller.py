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
from apps.core.services.eventos_service import EventosService

__version__ = "0.0.1"
__license__ = "AGPL V3"


def home(request):
    """
    Renderiza a página inicial com a listagem de todos os eventos.

    :param request: Objeto da requisição HTTP.
    :type request: HttpRequest
    :returns: Resposta HTTP com o template ``core/index.html`` e a lista de eventos.
    :rtype: HttpResponse
    """

    service = EventosService()
    eventos = service.listar_eventos()
    return render(request, "core/index.html", {"eventos": eventos})
