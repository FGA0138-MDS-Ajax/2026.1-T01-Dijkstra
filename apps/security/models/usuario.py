"""
apps.security.models.usuario
=============================
Models Django para o domínio de Usuarios e perfis de acesso.

Componentes Principais
----------------------
- TipoPerfil: Enum com os tipos de perfil disponiveis.
- Usuario: AbstractUser customizado, modelo central de autenticacao.
- Aluno: Proxy de Usuario com logica de inscricao em eventos.
- Organizador: Proxy de Usuario com logica de criacao de eventos.
- Gestor: Proxy de Usuario com logica de gestao de espacos fisicos.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

try:
    from typing import Self
except ImportError:  # Python < 3.11
    from typing import TypeVar
    Self = TypeVar("Self")  # type: ignore[assignment]

from django.contrib.auth.models import AbstractUser
from django.db import models

if TYPE_CHECKING:
    from apps.core.models import Evento, EspacoFisico, Inscricao

__version__ = "0.1.0"
__license__ = "AGPL V3"


class TipoPerfil(models.TextChoices):
    """Tipos de perfil de usuario no sistema."""

    ALUNO = "AL", "Aluno"
    ORGANIZADOR = "OR", "Organizador"
    GESTOR = "GE", "Gestor"
    ADMIN = "AD", "Administrador"


class Usuario(AbstractUser):
    """
    Modelo central de autenticacao do sistema.

    Substitui o User padrao do Django, utilizando UUID como PK
    e email como identificador unico de login.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, verbose_name="E-mail")
    nome_completo = models.CharField(max_length=255, verbose_name="Nome Completo")
    matricula = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Matricula"
    )
    foto = models.ImageField(
        upload_to="usuarios/fotos/", blank=True, null=True, verbose_name="Foto"
    )
    tipo = models.CharField(
        max_length=2,
        choices=TipoPerfil.choices,
        default=TipoPerfil.ALUNO,
        verbose_name="Tipo de Perfil",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "nome_completo"]

    class Meta:  # pylint: disable=too-few-public-methods
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.nome_completo or self.email

    @property
    def is_aluno(self):
        return self.tipo == TipoPerfil.ALUNO

    @property
    def is_organizador(self):
        return self.tipo == TipoPerfil.ORGANIZADOR

    @property
    def is_gestor(self):
        return self.tipo == TipoPerfil.GESTOR


class AlunoManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(tipo=TipoPerfil.ALUNO)


class Aluno(Usuario):
    """Proxy de Usuario com logica de dominio para alunos."""

    objects = AlunoManager()

    class Meta:  # pylint: disable=too-few-public-methods
        proxy = True
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"

    def realizar_inscricao(self, evento_id: uuid.UUID):
        from apps.core.models import Evento, Inscricao  # evita import circular
        evento = Evento.objects.get(pk=evento_id)
        if Inscricao.objects.filter(participante=self, evento=evento).exists():
            raise ValueError("Ja existe uma inscricao para este evento.")
        return Inscricao.objects.create(participante=self, evento=evento)

    def cancelar_inscricao(self, evento_id: uuid.UUID) -> bool:
        from apps.core.models import Inscricao  # evita import circular
        deleted, _ = Inscricao.objects.filter(
            participante=self, evento_id=evento_id
        ).delete()
        return deleted > 0


class OrganizadorManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(tipo=TipoPerfil.ORGANIZADOR)


class Organizador(Usuario):
    """Proxy de Usuario com logica de dominio para organizadores."""

    objects = OrganizadorManager()

    class Meta:  # pylint: disable=too-few-public-methods
        proxy = True
        verbose_name = "Organizador"
        verbose_name_plural = "Organizadores"

    def criar_evento(self, dados: dict):
        from apps.core.models import Evento  # evita import circular
        dados["organizador"] = self
        return Evento.objects.create(**dados)


class GestorManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(tipo=TipoPerfil.GESTOR)


class Gestor(Usuario):
    """Proxy de Usuario com logica de dominio para gestores."""

    objects = GestorManager()

    class Meta:  # pylint: disable=too-few-public-methods
        proxy = True
        verbose_name = "Gestor"
        verbose_name_plural = "Gestores"

    def cadastrar_espaco_fisico(self, dados: dict):
        from apps.core.models import EspacoFisico  # evita import circular
        return EspacoFisico.objects.create(**dados)
