"""Migration inicial do app core - cria todos os models de negocio."""

import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("security", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Organizacao",
            fields=[
                ("id", models.UUIDField(
                    primary_key=True, default=uuid.uuid4, editable=False, serialize=False
                )),
                ("nome", models.CharField(max_length=255, verbose_name="Nome")),
                ("descricao", models.TextField(verbose_name="Descricao")),
                ("foto", models.ImageField(
                    blank=True, null=True, upload_to="organizacoes/fotos/", verbose_name="Foto"
                )),
                ("membros", models.ManyToManyField(
                    blank=True,
                    related_name="organizacoes",
                    to=settings.AUTH_USER_MODEL,
                    verbose_name="Membros",
                )),
            ],
            options={
                "verbose_name": "Organizacao",
                "verbose_name_plural": "Organizacoes",
                "ordering": ["nome"],
            },
        ),
        
        migrations.CreateModel(
            name="Evento",
            fields=[
                ("id", models.UUIDField(
                    primary_key=True, default=uuid.uuid4, editable=False, serialize=False
                )),
                ("titulo", models.CharField(max_length=255, verbose_name="Titulo")),
                ("descricao", models.TextField(verbose_name="Descricao")),
                ("foto", models.ImageField(
                    blank=True, null=True, upload_to="eventos/fotos/", verbose_name="Foto"
                )),
                ("data_realizacao", models.DateTimeField(verbose_name="Data de Realizacao")),
                ("criado_em", models.DateTimeField(auto_now_add=True, verbose_name="Criado em")),
                ("organizador", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="eventos_criados",
                    to=settings.AUTH_USER_MODEL,
                    verbose_name="Organizador",
                )),
                ("organizacao", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="eventos",
                    to="core.organizacao",
                    verbose_name="Organizacao",
                )),
            ],
            options={
                "verbose_name": "Evento",
                "verbose_name_plural": "Eventos",
                "ordering": ["-data_realizacao"],
            },
        ),
        
        
        
    ]
