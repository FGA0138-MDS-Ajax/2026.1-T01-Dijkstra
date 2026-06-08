"""Controller HTTP para cadastro de novos usuários.

apps.security.controllers.cadastro_controller
==============================================
View de registro que processa o :class:`~apps.security.forms.CadastroForm`
e cria um novo :class:`~apps.security.models.usuario_models.Usuario`.

Notas
-----
- Requer Python >= 3.12
"""

from __future__ import annotations

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from apps.security.forms import CadastroForm

__version__ = "0.0.1"
__license__ = "AGPL V3"


@require_http_methods(["GET", "POST"])
def cadastro(request: HttpRequest) -> HttpResponse:
    """
    Exibe e processa o formulário de cadastro.

    GET  → renderiza o formulário vazio.
    POST → valida, cria o usuário e redireciona para o login.

    :param request: Objeto da requisição HTTP.
    :rtype: HttpResponse
    """
    if request.user.is_authenticated:
        return redirect("area-restrita-perfil")

    if request.method == "POST":
        form = CadastroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Conta criada com sucesso! Faça login para continuar.")
            return redirect("login")
    else:
        form = CadastroForm()

    return render(request, "security/cadastro.html", {"form": form})
