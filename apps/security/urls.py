"""Mapeamento de URLs do app security."""

from django.urls import path

from apps.security.controllers.usuario_controller import UsuarioController

urlpatterns = [
    path("usuarios/", UsuarioController.as_view(), name="usuarios-list"),
    path("usuarios/<str:usuario_id>/", UsuarioController.as_view(), name="usuarios-detail"),
]
