"""Migration inicial do app security."""

import uuid
import django.contrib.auth.models
import django.contrib.auth.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [("auth", "0012_alter_user_first_name_max_length")]
    operations = [
        migrations.CreateModel(
            name="Usuario",
            fields=[
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                ("is_superuser", models.BooleanField(default=False, verbose_name="superuser status")),
                ("username", models.CharField(
                    error_messages={"unique": "A user with that username already exists."},
                    max_length=150, unique=True,
                    validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                    verbose_name="username",
                )),
                ("first_name", models.CharField(blank=True, max_length=150, verbose_name="first name")),
                ("last_name", models.CharField(blank=True, max_length=150, verbose_name="last name")),
                ("is_staff", models.BooleanField(default=False, verbose_name="staff status")),
                ("is_active", models.BooleanField(default=True, verbose_name="active")),
                ("date_joined", models.DateTimeField(default=django.utils.timezone.now, verbose_name="date joined")),
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("email", models.EmailField(max_length=254, unique=True, verbose_name="E-mail")),
                ("nome_completo", models.CharField(max_length=255, verbose_name="Nome Completo")),
                ("matricula", models.CharField(blank=True, max_length=50, null=True, verbose_name="Matricula")),
                ("foto", models.ImageField(blank=True, null=True, upload_to="usuarios/fotos/", verbose_name="Foto")),
                ("tipo", models.CharField(
                    choices=[("AL","Aluno"),("OR","Organizador"),("GE","Gestor"),("AD","Administrador")],
                    default="AL", max_length=2, verbose_name="Tipo de Perfil",
                )),
                ("groups", models.ManyToManyField(
                    blank=True, related_name="user_set", related_query_name="user",
                    to="auth.group", verbose_name="groups",
                )),
                ("user_permissions", models.ManyToManyField(
                    blank=True, related_name="user_set", related_query_name="user",
                    to="auth.permission", verbose_name="user permissions",
                )),
            ],
            options={"verbose_name": "Usuario", "verbose_name_plural": "Usuarios"},
            managers=[("objects", django.contrib.auth.models.UserManager())],
        ),
        migrations.CreateModel(name="Aluno", fields=[],
            options={"proxy": True, "verbose_name": "Aluno", "verbose_name_plural": "Alunos"},
            bases=("security.usuario",),
        ),
        migrations.CreateModel(name="Organizador", fields=[],
            options={"proxy": True, "verbose_name": "Organizador", "verbose_name_plural": "Organizadores"},
            bases=("security.usuario",),
        ),
        migrations.CreateModel(name="Gestor", fields=[],
            options={"proxy": True, "verbose_name": "Gestor", "verbose_name_plural": "Gestores"},
            bases=("security.usuario",),
        ),
    ]
