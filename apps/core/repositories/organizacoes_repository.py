"""
apps.core.repositories.organizacoes_repository
===============================================
Repositorio de acesso a dados para o dominio de Organizacoes Esportivas.

Componentes Principais
----------------------
- OrganizacoesRepository: operacoes CRUD sobre Organizacao e UsuarioOrganizacao.

Notas
-----
- Requer Python >= 3.12
- Criado por Welder60 em 02 junho 2026
"""

from __future__ import annotations

import uuid
from typing import List, Optional

from django.contrib.auth import get_user_model

from apps.core.models.organizacoes_models import Organizacao, UsuarioOrganizacao

__version__ = "0.0.2"
__license__ = "AGPL V3"

Usuario = get_user_model()


class OrganizacoesRepository:
    """Repositorio para manipulacao de dados de Organizacoes Esportivas."""

    def create(self, data: dict) -> Organizacao:
        return Organizacao.objects.create(**data)

    def get_by_id(self, organizacao_id: uuid.UUID) -> Optional[Organizacao]:
        try:
            return Organizacao.objects.get(id=organizacao_id)
        except Organizacao.DoesNotExist:
            return None

    def get_all(self) -> List[Organizacao]:
        return list(Organizacao.objects.all())

    def update(self, organizacao_id: uuid.UUID, data: dict) -> Optional[Organizacao]:
        organizacao = self.get_by_id(organizacao_id)
        if organizacao is None:
            return None
        for campo, valor in data.items():
            setattr(organizacao, campo, valor)
        organizacao.save()
        return organizacao

    def delete(self, organizacao_id: uuid.UUID) -> bool:
        organizacao = self.get_by_id(organizacao_id)
        if organizacao is None:
            return False
        organizacao.delete()
        return True

    # ------------------------------------------------------------------
    # Membros (UsuarioOrganizacao)
    # ------------------------------------------------------------------

    def listar_membros(self, organizacao_id: uuid.UUID) -> List:
        """Retorna os vinculos UsuarioOrganizacao de uma organizacao."""
        return list(
            UsuarioOrganizacao.objects.filter(
                organizacao_id=organizacao_id
            ).select_related("usuario")
        )

    def adicionar_membro(self, organizacao_id: uuid.UUID, usuario_id: uuid.UUID) -> UsuarioOrganizacao:
        """Cria vinculo entre usuario e organizacao (ignora se ja existe)."""
        vinculo, _ = UsuarioOrganizacao.objects.get_or_create(
            organizacao_id=organizacao_id,
            usuario_id=usuario_id,
        )
        return vinculo

    def remover_membro(self, organizacao_id: uuid.UUID, usuario_id: uuid.UUID) -> bool:
        """Remove o vinculo entre usuario e organizacao."""
        deleted, _ = UsuarioOrganizacao.objects.filter(
            organizacao_id=organizacao_id,
            usuario_id=usuario_id,
        ).delete()
        return deleted > 0

    def listar_usuarios_sem_vinculo(self, organizacao_id: uuid.UUID) -> List:
        """Retorna usuarios que ainda nao sao membros da organizacao."""
        membros_ids = UsuarioOrganizacao.objects.filter(
            organizacao_id=organizacao_id
        ).values_list("usuario_id", flat=True)
        return list(Usuario.objects.exclude(id__in=membros_ids).order_by("nome_completo"))

    def listar_organizacoes_do_usuario(self, usuario_id: uuid.UUID) -> List[Organizacao]:
        """Retorna as organizacoes as quais o usuario esta vinculado."""
        ids = UsuarioOrganizacao.objects.filter(
            usuario_id=usuario_id
        ).values_list("organizacao_id", flat=True)
        return list(Organizacao.objects.filter(id__in=ids))
