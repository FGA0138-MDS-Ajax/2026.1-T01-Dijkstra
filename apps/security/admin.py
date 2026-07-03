"""
apps.security.admin
===================
Configuração e registro dos modelos de segurança administrativo do Django.
"""

from django.contrib import admin
from apps.security.models.usuario_models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    """Configuração do modelo de Usuário no Painel Admin."""

    list_display = ("username", "nome_completo", "tipo", "is_active", "is_staff")
    search_fields = ("username", "nome_completo", "matricula")
    list_filter = ("tipo", "is_active", "is_staff")
