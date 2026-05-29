"""
Migration para copiar imagens de static/media/eventos para media/eventos.
"""

import shutil
from pathlib import Path

from django.db import migrations


def copiar_midias(apps, schema_editor):
    from django.conf import settings

    src = Path(settings.BASE_DIR) / "static" / "media" / "eventos"
    dst = Path(settings.MEDIA_ROOT) / "eventos"

    if not src.exists():
        return

    dst.mkdir(parents=True, exist_ok=True)
    for arquivo in src.iterdir():
        destino = dst / arquivo.name
        if not destino.exists():
            shutil.copy2(arquivo, destino)


def reverter_midias(apps, schema_editor):
    pass  # não remove arquivos no rollback


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_dados_iniciais"),
    ]

    operations = [
        migrations.RunPython(copiar_midias, reverter_midias),
    ]
