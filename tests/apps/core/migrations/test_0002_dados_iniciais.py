from importlib import import_module
from unittest.mock import MagicMock


migration = import_module("apps.core.migrations.0002_dados_iniciais")


def test_remover_eventos():
    apps = MagicMock()

    evento_model = MagicMock()

    apps.get_model.return_value = evento_model

    migration.remover_eventos(
        apps,
        None,
    )

    nomes_esperados = [e["nome"] for e in migration.EVENTOS_INICIAIS]

    evento_model.objects.filter.assert_called_once_with(nome__in=nomes_esperados)

    evento_model.objects.filter.return_value.delete.assert_called_once()
