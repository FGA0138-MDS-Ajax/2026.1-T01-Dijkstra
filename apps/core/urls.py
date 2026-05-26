"""Mapeamento de URLs do app."""

from django.urls import path
from apps.core.controllers.eventos_controller import EventosController

urlpatterns = [
    path('eventos/', EventosController.as_view(), name='eventos-list'),
    path('eventos/<int:evento_id>/', EventosController.as_view(), name='eventos-detail'),
]
