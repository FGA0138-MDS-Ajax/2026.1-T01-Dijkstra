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
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from apps.core.models.espacos_models import EspacoFisico
from apps.core.models.reservas_models import ReservaEspaco
from apps.core.services.organizacoes_service import OrganizacoesService
from apps.security.models.usuario_models import TipoPerfil, Usuario

_org_service = OrganizacoesService()

__version__ = "0.0.1"
__license__ = "AGPL V3"

# Tipos de perfil aceitos por cada view
_ALUNO = "AL"
_ORGANIZADOR = "OR"
_GESTOR = "GE"


def _tem_acesso(user, tipo: str) -> bool:
    """Retorna True se o usuário é superuser ou possui o tipo de perfil."""
    return user.is_superuser or getattr(user, "tipo", None) == tipo


def _pode_gerenciar(gestor, alvo: Usuario) -> bool:
    """Retorna True se o gestor pode gerenciar o usuário alvo."""
    return not alvo.is_superuser and str(alvo.pk) != str(gestor.pk)


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
    organizacoes = _org_service.listar_organizacoes_do_usuario(request.user.id)
    return render(
        request,
        "security/area_restrita/organizacoes_vinculadas.html",
        {"organizacoes": organizacoes},
    )


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
    Exibe a página de Reservas de Espaços com filtros por status e espaço.

    Acessível a Gestores e superusers.

    Query params opcionais:
    - ``status``: filtra pelo status da reserva (pendente, aprovada, etc.)
    - ``espaco``: filtra pelo UUID do espaço físico

    :param request: Objeto da requisicao HTTP.
    :rtype: HttpResponse
    """
    if not _tem_acesso(request.user, _GESTOR):
        return redirect("area-restrita-perfil")

    status_filtro = request.GET.get("status", "")
    espaco_filtro = request.GET.get("espaco", "")

    qs = ReservaEspaco.objects.select_related(
        "espaco", "evento", "solicitante", "avaliador"
    ).order_by("-criado_em")

    if status_filtro in ReservaEspaco.Status.values:
        qs = qs.filter(status=status_filtro)

    if espaco_filtro:
        qs = qs.filter(espaco__id=espaco_filtro)

    espacos = EspacoFisico.objects.order_by("nome")

    return render(
        request,
        "security/area_restrita/reservas.html",
        {
            "reservas": qs,
            "espacos": espacos,
            "status_choices": ReservaEspaco.Status.choices,
            "status_filtro": status_filtro,
            "espaco_filtro": espaco_filtro,
        },
    )


@login_required
@require_http_methods(["GET"])
def gestao_usuarios(request: HttpRequest) -> HttpResponse:
    """
    Exibe a página de Gestão de Usuários com a lista de todos os usuários.

    Acessível a Gestores e superusers.

    :param request: Objeto da requisicao HTTP.
    :rtype: HttpResponse
    """
    if not _tem_acesso(request.user, _GESTOR):
        return redirect("area-restrita-perfil")
    usuarios = Usuario.objects.all().order_by("nome_completo")
    return render(
        request,
        "security/area_restrita/gestao_usuarios.html",
        {
            "usuarios": usuarios,
            "perfis": TipoPerfil.choices,
        },
    )


@login_required
@require_http_methods(["POST"])
def alterar_perfil_usuario(request: HttpRequest, usuario_id: str) -> HttpResponse:
    """
    Altera o tipo de perfil de um usuário.

    Acessível a Gestores e superusers.

    :param request: Objeto da requisicao HTTP.
    :param usuario_id: UUID do usuário a ser alterado.
    :rtype: HttpResponse
    """
    if not _tem_acesso(request.user, _GESTOR):
        return redirect("area-restrita-perfil")
    alvo = get_object_or_404(Usuario, pk=usuario_id)
    if not _pode_gerenciar(request.user, alvo):
        return redirect("area-restrita-gestao-usuarios")
    novo_tipo = request.POST.get("tipo", "")
    tipos_validos = [choice[0] for choice in TipoPerfil.choices]
    if novo_tipo in tipos_validos:
        alvo.tipo = novo_tipo
        alvo.save(update_fields=["tipo"])
    return redirect("area-restrita-gestao-usuarios")


@login_required
@require_http_methods(["POST"])
def inativar_usuario(request: HttpRequest, usuario_id: str) -> HttpResponse:
    """
    Ativa ou inativa um usuário (toggle).

    Acessível a Gestores e superusers.

    :param request: Objeto da requisicao HTTP.
    :param usuario_id: UUID do usuário a ser (in)ativado.
    :rtype: HttpResponse
    """
    if not _tem_acesso(request.user, _GESTOR):
        return redirect("area-restrita-perfil")
    alvo = get_object_or_404(Usuario, pk=usuario_id)
    if not _pode_gerenciar(request.user, alvo):
        return redirect("area-restrita-gestao-usuarios")
    alvo.is_active = not alvo.is_active
    alvo.save(update_fields=["is_active"])
    return redirect("area-restrita-gestao-usuarios")


@login_required
@require_http_methods(["POST"])
def excluir_usuario(request: HttpRequest, usuario_id: str) -> HttpResponse:
    """
    Exclui permanentemente um usuário.

    Acessível a Gestores e superusers.

    :param request: Objeto da requisicao HTTP.
    :param usuario_id: UUID do usuário a ser excluído.
    :rtype: HttpResponse
    """
    if not _tem_acesso(request.user, _GESTOR):
        return redirect("area-restrita-perfil")
    alvo = get_object_or_404(Usuario, pk=usuario_id)
    if not _pode_gerenciar(request.user, alvo):
        return redirect("area-restrita-gestao-usuarios")
    alvo.delete()
    return redirect("area-restrita-gestao-usuarios")
