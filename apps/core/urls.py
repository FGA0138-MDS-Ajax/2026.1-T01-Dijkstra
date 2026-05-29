"""Mapeamento de URLs do app core."""

from django.urls import path

from apps.core.controllers.eventos_controller import EventosController
from apps.core.controllers.home_controller import home
from apps.core.controllers.organizacao_controller import OrganizacaoController


urlpatterns = [
    path("", home, name="home"),
    path("eventos/", EventosController.as_view(), name="eventos-list"),
    path("eventos/<str:evento_id>/", EventosController.as_view(), name="eventos-detail"),
    path("organizacoes/", OrganizacaoController.as_view(), name="organizacoes-list"),
    path("organizacoes/<str:org_id>/", OrganizacaoController.as_view(), name="organizacoes-detail")   
]
