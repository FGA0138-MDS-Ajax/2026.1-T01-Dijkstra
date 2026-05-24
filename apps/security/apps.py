"""Configuração do app core."""

from django.apps import AppConfig


class SecurityConfig(AppConfig):
    """Configuração e metadados do app security."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.security"
