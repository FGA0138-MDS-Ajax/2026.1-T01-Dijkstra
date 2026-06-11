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
]
