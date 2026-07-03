"""
apps.security.repositories.usuarios_repositories
=================================================
Repositório de acesso a dados para o domínio de Usuários.

Componentes Principais
----------------------
- UsuarioRepository: Operações CRUD e consultas específicas sobre o modelo Usuario.

Notas
-----
- Requer Python >= 3.12
- Revisado por `Saresu <https://github.com/Saresu>`_ em 02 julho 2026
"""

from __future__ import annotations

import uuid
from typing import Any, List, Optional, Type

from django.db.models.query import QuerySet

from apps.security.models.usuario_models import Usuario

__version__ = "0.0.2"
__license__ = "AGPL V3"


class UsuarioRepository:
    """Repositório para manipulação e persistência de dados de Usuários."""

    model: Type[Usuario]

    def __init__(self) -> None:
        """Inicializa o repositório definindo o modelo alvo."""
        self.model = Usuario

    def create_usuario(self, usuario_data: dict[str, Any]) -> Usuario:
        """Cria e persiste um novo Usuário com os dados fornecidos."""
        return self.model.objects.create(**usuario_data)

    def get_usuario_by_id(self, usuario_id: uuid.UUID | str) -> Optional[Usuario]:
        """Busca um Usuário pelo seu identificador único UUID."""
        try:
            return self.model.objects.get(id=usuario_id)
        except self.model.DoesNotExist:
            return None

    def get_all_usuarios(self) -> List[Usuario]:
        """Retorna uma lista contendo todos os usuários cadastrados."""
        return list(self.model.objects.all())

    def get_organizadores_usuarios(self) -> QuerySet[Usuario]:
        """Retorna um QuerySet filtrado com usuários do tipo Organizador ('OR')."""
        return self.model.objects.filter(tipo="OR")

    def update_usuario(
        self, usuario_id: uuid.UUID | str, usuario_data: dict[str, Any]
    ) -> Optional[Usuario]:
        """Atualiza os campos de um Usuário existente."""
        usuario = self.get_usuario_by_id(usuario_id)
        if usuario is None:
            return None
        for key, value in usuario_data.items():
            setattr(usuario, key, value)
        usuario.save()
        return usuario

    def delete_usuario(self, usuario_id: uuid.UUID | str) -> bool:
        """Remove permanentemente um Usuário do sistema pelo ID."""
        usuario = self.get_usuario_by_id(usuario_id)
        if usuario is None:
            return False
        usuario.delete()
        return True
