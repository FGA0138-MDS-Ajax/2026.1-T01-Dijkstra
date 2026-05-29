"""apps.core.controllers.home_controller - View da pagina inicial."""

from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Q

from apps.core.models import Evento

EVENTOS_POR_PAGINA = 6


def home(request):
    """
    Renderiza a pagina inicial com listagem de eventos.

    Query params suportados:
      - q: texto livre para busca no titulo/descricao
      - data_inicio: filtro de data minima (YYYY-MM-DD)
      - data_fim: filtro de data maxima (YYYY-MM-DD)
      - page: numero da pagina (padrao 1)
    """
    q = request.GET.get("q", "").strip()
    data_inicio = request.GET.get("data_inicio", "").strip()
    data_fim = request.GET.get("data_fim", "").strip()

    qs = Evento.objects.select_related("organizador", "organizacao").order_by("data_realizacao")

    if q:
        qs = qs.filter(Q(titulo__icontains=q) | Q(descricao__icontains=q))

    if data_inicio:
        qs = qs.filter(data_realizacao__date__gte=data_inicio)

    if data_fim:
        qs = qs.filter(data_realizacao__date__lte=data_fim)

    paginator = Paginator(qs, EVENTOS_POR_PAGINA)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    return render(request, "core/index.html", {
        "page_obj": page_obj,
        "q": q,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
    })
