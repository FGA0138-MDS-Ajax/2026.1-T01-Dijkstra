"""Configuração do app security."""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuração e metadados do app core."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
