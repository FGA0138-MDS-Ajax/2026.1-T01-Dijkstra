from importlib import import_module
from unittest.mock import MagicMock

migration = import_module(
    "apps.core.migrations.0013_evento_vinculo_organizador_organizacao"
)


def _mock_apps(eventos):
    apps = MagicMock()

    usuario_model = MagicMock()
    usuario_model.objects.get_or_create.return_value = (
        MagicMock(id="org-padrao-id"),
        True,
    )

    organizacao_model = MagicMock()
    organizacao_model.objects.get_or_create.return_value = (
        MagicMock(id="organizacao-id"),
        True,
    )

    evento_model = MagicMock()
    evento_model.objects.all.return_value = eventos

    def get_model(app_label, nome):
        return {
            ("core", "Evento"): evento_model,
            ("core", "Organizacao"): organizacao_model,
            ("security", "Usuario"): usuario_model,
        }.get((app_label, nome), MagicMock())

    apps.get_model.side_effect = get_model
    return apps, evento_model, organizacao_model, usuario_model


def test_converter_eventos_organizador_vazio_usa_nome_padrao():
    """Cobre o ramo 'nome_org = \"Organização Padrão\"' quando o texto está vazio."""
    evento_sem_organizador = MagicMock()
    evento_sem_organizador.organizador = "   "

    apps, evento_model, organizacao_model, usuario_model = _mock_apps(
        [evento_sem_organizador]
    )

    migration.converter_eventos(apps, None)

    organizacao_model.objects.get_or_create.assert_called_once_with(
        nome="Organização Padrão",
        defaults={"descricao": migration.DESCRICAO_ORG_AUTOMATICA},
    )
    evento_sem_organizador.save.assert_called_once_with(
        update_fields=["organizacao", "organizador_fk"]
    )


def test_converter_eventos_usa_nome_do_organizador():
    evento_com_organizador = MagicMock()
    evento_com_organizador.organizador = "Atlética Central"

    apps, evento_model, organizacao_model, usuario_model = _mock_apps(
        [evento_com_organizador]
    )

    migration.converter_eventos(apps, None)

    organizacao_model.objects.get_or_create.assert_called_once_with(
        nome="Atlética Central",
        defaults={"descricao": migration.DESCRICAO_ORG_AUTOMATICA},
    )


def test_reverter_eventos_com_organizacao():
    evento = MagicMock()
    evento.organizacao_id = "algum-id"
    evento.organizacao.nome = "Atlética Reversa"

    apps = MagicMock()
    evento_model = MagicMock()
    evento_model.objects.all.return_value = [evento]
    apps.get_model.return_value = evento_model

    migration.reverter_eventos(apps, None)

    assert evento.organizador == "Atlética Reversa"
    evento.save.assert_called_once_with(update_fields=["organizador"])


def test_reverter_eventos_sem_organizacao():
    evento = MagicMock()
    evento.organizacao_id = None

    apps = MagicMock()
    evento_model = MagicMock()
    evento_model.objects.all.return_value = [evento]
    apps.get_model.return_value = evento_model

    migration.reverter_eventos(apps, None)

    assert evento.organizador == ""
    evento.save.assert_called_once_with(update_fields=["organizador"])
