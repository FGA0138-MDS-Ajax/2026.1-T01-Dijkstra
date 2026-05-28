from django.shortcuts import render
from apps.core.services.eventos_service import EventosService


def home(request):
    service = EventosService()
    eventos = service.listar_eventos()
    return render(request, "core/index.html", {"eventos": eventos})
