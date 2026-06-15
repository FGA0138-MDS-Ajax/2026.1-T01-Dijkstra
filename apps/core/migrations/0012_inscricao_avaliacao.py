"""Migration: adiciona avaliador, data_avaliacao e motivo_reprovacao à Inscricao."""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0011_usuarioorganizacao"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="inscricao",
            name="avaliador",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="inscricoes_avaliadas",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Avaliador",
            ),
        ),
        migrations.AddField(
            model_name="inscricao",
            name="data_avaliacao",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="Data da Avaliação",
            ),
        ),
        migrations.AddField(
            model_name="inscricao",
            name="motivo_reprovacao",
            field=models.TextField(
                blank=True,
                null=True,
                verbose_name="Motivo da Reprovação",
            ),
        ),
    ]
