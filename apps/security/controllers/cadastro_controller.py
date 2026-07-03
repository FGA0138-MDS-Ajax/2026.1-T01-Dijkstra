"""Controller HTTP para cadastro de novos usuários.

apps.security.controllers.cadastro_controller
==============================================
View de registro que processa o :class:`~apps.security.forms.CadastroForm`
e cria um novo :class:`~apps.security.models.usuario_models.Usuario`
seguindo o princípio de minimização de dados (LGPD / US-012).

Notas
-----
- Requer Python >= 3.12
- Revisado por `Saresu <https://github.com/Saresu>`_ em 02 julho 2026
"""

from __future__ import annotations

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit

from apps.security.forms import CadastroForm

__version__ = "0.0.3"
__license__ = "AGPL V3"


# Sintaxe robusta: Conta qualquer requisição (GET ou POST) no limite de 5 por minuto.
@ratelimit(key="ip", rate="5/m", block=True)
@require_http_methods(["GET", "POST"])
def cadastro(request: HttpRequest) -> HttpResponse:
    """
    Exibe e processa o formulário de cadastro simplificado.

    GET  → renderiza o formulário vazio.
    POST → valida a matrícula e senhas, cria o usuário com privilégios
           mínimos e redireciona para o login.

    Possui proteção anti-bot via rate limiting (máximo de 5 tentativas por minuto por IP).

    :param request: Objeto da requisição HTTP.
    :rtype: HttpResponse
    """
    if request.user.is_authenticated:
        return redirect("area-restrita-perfil")

    if request.method == "POST":
        form = CadastroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Conta criada com sucesso! Faça login para continuar."
            )
            return redirect("login")
    else:
        form = CadastroForm()

    return render(request, "security/cadastro.html", {"form": form})
