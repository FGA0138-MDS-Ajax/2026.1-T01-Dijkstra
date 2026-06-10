"""Formulários do app security.

apps.security.forms
===================
Formulários de autenticação e registro de usuários.

Componentes Principais
----------------------
- :class:`CadastroForm`: valida e cria um novo :class:`~apps.security.models.usuario_models.Usuario`
  baseado na política de minimização de dados (LGPD).

Notas
-----
- Requer Python >= 3.12
"""

from __future__ import annotations

from django import forms
from django.contrib.auth.hashers import make_password

from apps.security.models.usuario_models import TipoPerfil, Usuario

__version__ = "0.0.2"
__license__ = "AGPL V3"


class CadastroForm(forms.Form):
    """Formulário de registro simplificado de novo usuário."""

    matricula = forms.CharField(
        max_length=20,
        required=True,
        label="Matrícula",
        widget=forms.TextInput(attrs={"class": "auth-input", "placeholder": "Sua matrícula institucional"}),
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
    termos_uso = forms.BooleanField(
        required=True,
        label="Termos de Uso",
        error_messages={'required': 'Você deve aceitar os Termos de Uso para criar a conta.'},
    )

    def clean_matricula(self) -> str:
        """Verifica se a matrícula já está em uso no sistema."""
        matricula = self.cleaned_data["matricula"]
        # A matrícula será salva no banco como o username de autenticação
        if Usuario.objects.filter(username=matricula).exists():
            raise forms.ValidationError("Esta matrícula já está cadastrada no sistema.")
        return matricula

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

        Mapeia a matrícula para o username e define configurações de segurança padrão.

        :returns: Instância do usuário criado.
        :rtype: Usuario
        """
        data = self.cleaned_data
        return Usuario.objects.create(
            username=data["matricula"],
            matricula=data["matricula"],
            nome_completo=f"Usuário {data['matricula']}",  # Fallback de nome obrigatório no banco
            tipo=TipoPerfil.ALUNO,  # Perfil padrão (mínimo privilégio)
            password=make_password(data["password"]),
            is_active=True,
        )