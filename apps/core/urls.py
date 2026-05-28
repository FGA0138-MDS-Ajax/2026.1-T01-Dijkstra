"""Mapeamento de URLs do app."""

from django.urls import path
from apps.core.controllers.eventos_controller import EventosController
from apps.core.controllers.home_controller import home

urlpatterns = [
    path('', home, name='home'),
    path('eventos/', EventosController.as_view(), name='eventos-list'),
    path('eventos/<int:evento_id>/', EventosController.as_view(), name='eventos-detail'),
]
