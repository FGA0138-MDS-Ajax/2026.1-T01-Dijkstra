"""Formulários do app security.

apps.security.forms
===================
Formulários de autenticação e registro de usuários.

Componentes Principais
----------------------
- :class:`CadastroForm`: valida e cria um novo :class:`~apps.security.models.usuario_models.Usuario`.

Notas
-----
- Requer Python >= 3.12
"""

from __future__ import annotations

from django import forms
from django.contrib.auth.hashers import make_password

from apps.security.models.usuario_models import TipoPerfil, Usuario

__version__ = "0.0.1"
__license__ = "AGPL V3"

# Perfis disponíveis para auto-cadastro
_TIPOS_CADASTRO = [
    (TipoPerfil.ALUNO, "Aluno"),
    (TipoPerfil.ORGANIZADOR, "Organizador"),
    (TipoPerfil.GESTOR, "Gestor"),
]


class CadastroForm(forms.Form):
    """Formulário de registro de novo usuário."""

    nome_completo = forms.CharField(
        max_length=255,
        label="Nome completo",
        widget=forms.TextInput(attrs={"class": "auth-input", "placeholder": "Seu nome completo"}),
    )
    username = forms.CharField(
        max_length=150,
        label="Usuário",
        widget=forms.TextInput(attrs={"class": "auth-input", "placeholder": "Nome de usuário"}),
    )
    email = forms.EmailField(
        required=False,
        label="E-mail",
        widget=forms.EmailInput(attrs={"class": "auth-input", "placeholder": "seu@email.com"}),
    )
    matricula = forms.CharField(
        max_length=20,
        required=False,
        label="Matrícula",
        widget=forms.TextInput(attrs={"class": "auth-input", "placeholder": "Opcional"}),
    )
    tipo = forms.ChoiceField(
        choices=_TIPOS_CADASTRO,
        label="Tipo de perfil",
        widget=forms.RadioSelect(),
        initial=TipoPerfil.ALUNO,
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={"class": "auth-input", "placeholder": "Mínimo 8 caracteres"}),
        min_length=8,
    )
    confirmar_senha = forms.CharField(
        label="Confirmar senha",
        widget=forms.PasswordInput(attrs={"class": "auth-input", "placeholder": "Repita a senha"}),
    )

    def clean_username(self) -> str:
        """Verifica se o nome de usuário já está em uso."""
        username = self.cleaned_data["username"]
        if Usuario.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nome de usuário já está em uso.")
        return username

    def clean(self) -> dict:
        """Verifica se as senhas coincidem."""
        cleaned = super().clean()
        password = cleaned.get("password")
        confirmar = cleaned.get("confirmar_senha")
        if password and confirmar and password != confirmar:
            self.add_error("confirmar_senha", "As senhas não coincidem.")
        return cleaned

    def save(self) -> Usuario:
        """
        Cria e salva o novo usuário.

        :returns: Instância do usuário criado.
        :rtype: Usuario
        """
        data = self.cleaned_data
        return Usuario.objects.create(
            username=data["username"],
            nome_completo=data["nome_completo"],
            email=data.get("email", ""),
            matricula=data.get("matricula") or None,
            tipo=data["tipo"],
            password=make_password(data["password"]),
        )
