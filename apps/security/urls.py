"""
Mapeamento de URLs do app.

- Lint por `Saresu <https://github.com/Saresu>`_ em 05 junho 2026
"""

# compatibilidade
from __future__ import annotations

from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from apps.security.controllers.cadastro import cadastro

from apps.security.controllers.cadastro_controller import cadastro
from apps.security.controllers.area_restrita_controller import (
    area_restrita_redirect,
    perfil,
    eventos_inscritos,
    gestao_eventos_restrita,
    organizacoes_vinculadas,
    espacos_esportivos,
    reservas,
    gestao_usuarios,
    alterar_perfil_usuario,
    inativar_usuario,
    excluir_usuario,
)

from apps.security.controllers.cadastro_controller import cadastro
from apps.security.controllers.area_restrita_controller import (
    area_restrita_redirect,
    perfil,
    eventos_inscritos,
    gestao_eventos_restrita,
    organizacoes_vinculadas,
    espacos_esportivos,
    reservas,
    gestao_usuarios,
    alterar_perfil_usuario,
    inativar_usuario,
    excluir_usuario,
)

urlpatterns = [
    # Rota de Login
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="security/login.html"),
        name="login",
    ),
    # Rota de Logout
    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),
    # Rota temporária de Cadastro (Apenas para não dar erro no botão)
    path(
    "cadastro/",
    cadastro,
    name="cadastro",
),
    # Rota de recuperação de senha
    path(
        "esqueci-senha/",
        TemplateView.as_view(template_name="security/esqueci_senha.html"),
        name="esqueceu_senha",
    ),
    # Área Restrita
    path("area-restrita/", area_restrita_redirect, name="area-restrita"),
    path("area-restrita/perfil/", perfil, name="area-restrita-perfil"),
    path(
        "area-restrita/eventos-inscritos/",
        eventos_inscritos,
        name="area-restrita-eventos-inscritos",
    ),
    path(
        "area-restrita/gestao-eventos/",
        gestao_eventos_restrita,
        name="area-restrita-gestao-eventos",
    ),
    path(
        "area-restrita/organizacoes-vinculadas/",
        organizacoes_vinculadas,
        name="area-restrita-organizacoes-vinculadas",
    ),
    path(
        "area-restrita/espacos-esportivos/",
        espacos_esportivos,
        name="area-restrita-espacos-esportivos",
    ),
    path("area-restrita/reservas/", reservas, name="area-restrita-reservas"),
    path(
        "area-restrita/gestao-usuarios/",
        gestao_usuarios,
        name="area-restrita-gestao-usuarios",
    ),
    path(
        "area-restrita/gestao-usuarios/<str:usuario_id>/alterar-perfil/",
        alterar_perfil_usuario,
        name="area-restrita-alterar-perfil-usuario",
    ),
    path(
        "area-restrita/gestao-usuarios/<str:usuario_id>/inativar/",
        inativar_usuario,
        name="area-restrita-inativar-usuario",
    ),
    path(
        "area-restrita/gestao-usuarios/<str:usuario_id>/excluir/",
        excluir_usuario,
        name="area-restrita-excluir-usuario",
    ),
]
