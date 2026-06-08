"""Controller HTTP para a Área Restrita do sistema.

apps.security.controllers.area_restrita_controller
===================================================
Views da área restrita com subnav por perfil de usuário.

Componentes Principais
----------------------
- :func:`area_restrita_redirect`: redireciona ``/area-restrita/`` para Meu Perfil.
- :func:`perfil`: página Meu Perfil (todos os autenticados).
- :func:`eventos_inscritos`: página de eventos inscritos (Aluno).
- :func:`gestao_eventos_restrita`: gestão de eventos (Organizador).
- :func:`organizacoes_vinculadas`: organizações vinculadas (Organizador).
- :func:`espacos_esportivos`: espaços esportivos (Gestor).
- :func:`reservas`: reservas de espaços (Gestor).
- :func:`gestao_usuarios`: gestão de usuários (Gestor).

Notas
-----
- Requer Python >= 3.12
- Acesso restrito via ``@login_required`` e verificação de perfil.
"""

from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

__version__ = "0.0.1"
__license__ = "AGPL V3"

# Tipos de perfil aceitos por cada view
_ALUNO = "AL"
_ORGANIZADOR = "OR"
_GESTOR = "GE"


def _tem_acesso(user, tipo: str) -> bool:
    """Retorna True se o usuário é superuser ou possui o tipo de perfil."""
    return user.is_superuser or getattr(user, "tipo", None) == tipo


@login_required
@require_http_methods(["GET"])
def area_restrita_redirect(request: HttpRequest) -> HttpResponse:
    """Redireciona a raiz da área restrita para Meu Perfil."""
    return redirect("area-restrita-perfil")


@login_required
@require_http_methods(["GET"])
def perfil(request: HttpRequest) -> HttpResponse:
    """
    Exibe a página Meu Perfil.

    Acessível a todos os usuários autenticados.

    :param request: Objeto da requisicao HTTP.
    :rtype: HttpResponse
    """
    return render(request, "security/area_restrita/perfil.html")


@login_required
@require_http_methods(["GET"])
def eventos_inscritos(request: HttpRequest) -> HttpResponse:
    """
    Exibe a página de Eventos Inscritos.

    Acessível a Alunos e superusers.

    :param request: Objeto da requisicao HTTP.
    :rtype: HttpResponse
    """
    if not _tem_acesso(request.user, _ALUNO):
        return redirect("area-restrita-perfil")
    return render(request, "security/area_restrita/eventos_inscritos.html")


@login_required
@require_http_methods(["GET"])
def gestao_eventos_restrita(request: HttpRequest) -> HttpResponse:
    """
    Exibe a página de Gestão de Eventos da área restrita.

    Acessível a Organizadores e superusers.

    :param request: Objeto da requisicao HTTP.
    :rtype: HttpResponse
    """
    if not _tem_acesso(request.user, _ORGANIZADOR):
        return redirect("area-restrita-perfil")
    return render(request, "security/area_restrita/gestao_eventos.html")


@login_required
@require_http_methods(["GET"])
def organizacoes_vinculadas(request: HttpRequest) -> HttpResponse:
    """
    Exibe a página de Organizações Vinculadas.

    Acessível a Organizadores e superusers.

    :param request: Objeto da requisicao HTTP.
    :rtype: HttpResponse
    """
    if not _tem_acesso(request.user, _ORGANIZADOR):
        return redirect("area-restrita-perfil")
    return render(request, "security/area_restrita/organizacoes_vinculadas.html")


@login_required
@require_http_methods(["GET"])
def espacos_esportivos(request: HttpRequest) -> HttpResponse:
    """
    Exibe a página de Espaços Esportivos.

    Acessível a Gestores e superusers.

    :param request: Objeto da requisicao HTTP.
    :rtype: HttpResponse
    """
    if not _tem_acesso(request.user, _GESTOR):
        return redirect("area-restrita-perfil")
    return render(request, "security/area_restrita/espacos_esportivos.html")


@login_required
@require_http_methods(["GET"])
def reservas(request: HttpRequest) -> HttpResponse:
    """
    Exibe a página de Reservas de Espaços.

    Acessível a Gestores e superusers.

    :param request: Objeto da requisicao HTTP.
    :rtype: HttpResponse
    """
    if not _tem_acesso(request.user, _GESTOR):
        return redirect("area-restrita-perfil")
    return render(request, "security/area_restrita/reservas.html")


@login_required
@require_http_methods(["GET"])
def gestao_usuarios(request: HttpRequest) -> HttpResponse:
    """
    Exibe a página de Gestão de Usuários.

    Acessível a Gestores e superusers.

    :param request: Objeto da requisicao HTTP.
    :rtype: HttpResponse
    """
    if not _tem_acesso(request.user, _GESTOR):
        return redirect("area-restrita-perfil")
    return render(request, "security/area_restrita/gestao_usuarios.html")
