# Generated manually on 2026-06-11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0010_reservaespaco"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UsuarioOrganizacao",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="organizacoes_vinculadas",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Usuário",
                    ),
                ),
                (
                    "organizacao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="membros",
                        to="core.organizacao",
                        verbose_name="Organização",
                    ),
                ),
            ],
            options={
                "verbose_name": "Membro de Organização",
                "verbose_name_plural": "Membros de Organizações",
                "unique_together": {("usuario", "organizacao")},
            },
        ),
    ]
